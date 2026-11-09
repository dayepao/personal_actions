"""在 VS Code 中直接运行本文件，无需命令行参数或第三方依赖。"""

import queue
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from layout import LayoutError, atomic_save, load_layout, make_layout, plan_restore, verify_positions
from shell_api import DesktopShell, ShellError, enable_dpi_awareness

# PyInstaller 单文件模式下 __file__ 位于临时解压目录。
# 用户布局必须使用实际 EXE 的目录，不能随临时文件在退出时被清理。
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LAYOUT_PATH = APP_DIR / "layout.json"


def state_environment(state):
    return state["view"], state["monitors"], state["auto_arrange"]


def positions(state):
    return {i["id"]: i["position"] for i in state["icons"]}


def save_layout(path=LAYOUT_PATH, shell_factory=DesktopShell):
    with shell_factory() as desktop:
        state = desktop.snapshot()
        data = make_layout(state)
        # 再读一次以防枚举期间用户拖动图标或插拔显示器。
        fresh = desktop.snapshot()
        if state_environment(state) != state_environment(fresh) or positions(state) != positions(fresh):
            raise LayoutError("读取期间桌面状态发生变化，请稍后重新保存。")
        atomic_save(path, data)
    note = " 当前启用了自动排列，恢复前请手动关闭。" if state["auto_arrange"] else ""
    return f"保存成功：{len(data['icons'])} 个图标。再次保存会更新基准布局。{note}"


def restore_layout(path=LAYOUT_PATH, shell_factory=DesktopShell, pause=time.sleep):
    saved = load_layout(path)  # JSON 有问题时连移动接口都不进入。
    with shell_factory() as desktop:
        before = desktop.snapshot()  # 临时回退基准仅在内存中，不覆盖 layout.json。
        plan = plan_restore(saved, before)
        fresh = desktop.snapshot()
        if state_environment(before) != state_environment(fresh) or positions(before) != positions(fresh):
            raise LayoutError("计算期间桌面状态发生变化，请稍后重试；未移动图标。")
        target = plan["positions"]
        # 容差限制在很小的物理像素范围，不会把相邻格误判为成功。
        tolerance = min(8, max(2, min(before["view"]["spacing"]) // 16))
        try:
            if positions(before) != target:
                desktop.move(target)
            errors = []
            for attempt in range(6):
                after = desktop.snapshot()
                if state_environment(before) != state_environment(after):
                    raise LayoutError("恢复期间显示环境或视图设置发生变化。")
                errors = verify_positions(after, target, tolerance)
                if not errors:
                    break
                if attempt != 5:
                    pause(0.15)  # 给 Explorer 批量定位/网格吸附留出完成时间。
            if errors:
                raise LayoutError("；".join(errors[:5]) + (f"（共 {len(errors)} 项）" if len(errors) > 5 else ""))
        except Exception as error:
            rollback = ""
            try:
                actual = desktop.snapshot()
                if state_environment(actual) != state_environment(before):
                    rollback = "显示环境已改变，为防止错误坐标移动，未执行回退。"
                else:
                    baseline = positions(before)
                    survivors = {key: point for key, point in baseline.items() if key in positions(actual)}
                    desktop.move(survivors)
                    problems = []
                    for attempt in range(6):
                        reverted = desktop.snapshot()
                        problems = verify_positions(reverted, baseline, tolerance, check_geometry=False)
                        if not problems:
                            break
                        if attempt != 5:
                            pause(0.15)
                    rollback = "已回退并核对操作前的位置。" if not problems else "已尝试回退，但未完全恢复：" + "；".join(problems[:3])
            except Exception as rollback_error:
                rollback = f"回退未完成：{rollback_error}"
            raise LayoutError(f"恢复失败：{error}\n{rollback}\n保存文件未修改。") from error
    kind = "单屏布局已映射到当前主屏" if plan["single_screen"] else "跨屏布局已按设备匹配"
    return (
        f"恢复成功并已回读验证：{kind}。\n"
        f"已有 {plan['existing']} 个，缺失 {plan['missing']} 个，新增 {plan['added']} 个；"
        f"保留空位 {plan['reserved']} 个。" + ("\n" + " ".join(plan["notes"]) if plan["notes"] else "")
    )


class Application:
    def __init__(self, root):
        self.root, self.busy = root, False
        self.results = queue.Queue()
        root.title("DesktopLayout")
        root.resizable(False, False)
        frame = ttk.Frame(root, padding=22)
        frame.grid()
        ttk.Label(frame, text="桌面图标布局", font=("Microsoft YaHei UI", 15)).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))
        self.buttons = [
            ttk.Button(frame, text="保存布局", command=lambda: self.start(save_layout)),
            ttk.Button(frame, text="恢复布局", command=lambda: self.start(restore_layout)),
        ]
        for index, button in enumerate(self.buttons):
            button.grid(row=1, column=index, padx=(0, 12), pady=(0, 18), ipadx=24, ipady=8)
        self.saved = tk.StringVar()
        self.status = tk.StringVar(value="就绪。请在排好图标后保存布局。")
        ttk.Label(frame, textvariable=self.saved, justify="left", wraplength=520).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 14))
        ttk.Separator(frame).grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Label(frame, textvariable=self.status, justify="left", wraplength=520).grid(row=4, column=0, columnspan=2, sticky="w", pady=(14, 0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh_saved()

    def refresh_saved(self):
        if not LAYOUT_PATH.exists():
            self.saved.set("已保存布局：无\n上次保存：—\n图标数量：0")
            return
        try:
            data = load_layout(LAYOUT_PATH)
            self.saved.set(f"已保存布局：有\n上次保存：{data['saved_at']}\n图标数量：{len(data['icons'])}")
        except (OSError, LayoutError) as error:
            self.saved.set(f"已保存布局：文件存在但无法读取\n{error}")

    def start(self, operation):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.state(["disabled"])
        self.status.set("正在保存…" if operation is save_layout else "正在计算并恢复布局…")

        def work():
            try:
                # worker 创建自己的 STA；COM 接口和 PIDL 不跨线程传递。
                enable_dpi_awareness()
                self.results.put((True, operation()))
            except Exception as error:
                self.results.put((False, str(error) or type(error).__name__))

        threading.Thread(target=work, name="DesktopLayout-operation", daemon=False).start()
        self.root.after(80, self.poll)

    def poll(self):
        try:
            success, result = self.results.get_nowait()
        except queue.Empty:
            self.root.after(80, self.poll)
            return
        self.busy = False
        for button in self.buttons:
            button.state(["!disabled"])
        self.refresh_saved()
        self.status.set(result)
        if not success:
            messagebox.showerror("DesktopLayout", result, parent=self.root)

    def close(self):
        if self.busy:
            self.status.set("正在完成操作与验证，请稍候再关闭窗口。")
        else:
            self.root.destroy()


def main():
    try:
        enable_dpi_awareness()
    except (ShellError, OSError) as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("DesktopLayout", str(error), parent=root)
        root.destroy()
        return
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()

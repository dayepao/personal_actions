"""真实 Windows 桌面检查：可在 VS Code 直接运行；默认只读。

需要验证实际移动时，将下面 RUN_MOVEMENT_CHECK 改成 True 再运行。
会临时交换两个图标并恢复，也会将一个现有图标作为“新增图标”测试列优先分配。
始终保留原桌面快照用于 finally 回退；不重启 Explorer、不操作桌面文件内容。
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from layout import atomic_save, grid_position, make_layout, plan_restore, shell_point, verify_positions
from main import positions, restore_layout, save_layout
from shell_api import DesktopShell, enable_dpi_awareness

RUN_MOVEMENT_CHECK = False


def run(movement=False):
    enable_dpi_awareness()
    with DesktopShell() as desktop:
        baseline = desktop.snapshot()
        saved = make_layout(baseline)
        plan = plan_restore(saved, baseline)
        print(f"真实桌面：{len(baseline['icons'])} 个图标，{len(baseline['monitors'])} 台显示器。")
        print(f"视图信息：{baseline['view']}")
        print(f"同环境精确恢复计划：{plan['positions'] == positions(baseline)}")
        problems = verify_positions(baseline, plan["positions"])
        if problems:
            raise RuntimeError("当前桌面已有越界/冲突，请先手动整理后验证：" + "；".join(problems))
    if not movement:
        print("只读检查通过。没有移动任何图标。")
        return
    if len(baseline["icons"]) < 2:
        raise RuntimeError("移动检查需要至少两个图标。")

    project = Path(__file__).resolve().parents[1]
    # 测试文件仅放在项目内；从不覆盖用户的 layout.json。
    with tempfile.TemporaryDirectory(prefix=".desktoplayout-check-", dir=project) as directory:
        path = Path(directory) / "layout.json"
        atomic_save(path, saved)
        try:
            with DesktopShell() as desktop:
                current = desktop.snapshot()
                if positions(current) != positions(baseline):
                    raise RuntimeError("测试前桌面已发生变化，停止移动。")
                one, two = baseline["icons"][:2]
                swapped = positions(baseline)
                swapped[one["id"]], swapped[two["id"]] = swapped[two["id"]], swapped[one["id"]]
                desktop.move(swapped)
                after = desktop.snapshot()
                errors = verify_positions(after, swapped, tolerance=2)
                if errors:
                    raise RuntimeError("实际交换验证失败：" + "；".join(errors))
            print("真实 COM 批量交换两个图标并回读：通过。")
            print(restore_layout(path))
            print(restore_layout(path))
            with DesktopShell() as desktop:
                after = desktop.snapshot()
                if positions(after) != positions(baseline):
                    raise RuntimeError("重复恢复后的坐标与原桌面不一致。")
            print("真实恢复及重复恢复精确坐标：通过。")
            secondary = next((m for m in baseline["monitors"] if not m["primary"]), None)
            if secondary:
                with DesktopShell() as desktop:
                    current = desktop.snapshot()
                    across = positions(current)
                    across[one["id"]] = shell_point(grid_position(secondary, current["view"], [1, 1]), current["view"])
                    desktop.move(across)
                    on_both = desktop.snapshot()
                    errors = verify_positions(on_both, across, tolerance=2)
                    if errors:
                        raise RuntimeError("真实副屏定位失败：" + "；".join(errors))
                    multi_saved = make_layout(on_both)
                    atomic_save(path, multi_saved)
                    desktop.move(positions(baseline))
                print(restore_layout(path))
                print("真实跨屏保存、按设备恢复与副屏定位：通过。")
                atomic_save(path, saved)
                print(restore_layout(path))
            # 只改临时 JSON 基准，不创建/删除实际文件，真实 Shell 负责位置操作。
            reduced = make_layout(baseline)
            reduced["icons"] = [i for i in reduced["icons"] if i["id"] != one["id"]]
            atomic_save(path, reduced)
            print(restore_layout(path))
            print("以真实现有图标验证新增图标网格分配：通过（没有新增文件）。")
            atomic_save(path, saved)
            print(restore_layout(path))
            print(save_layout(path))
        finally:
            # 无论测试中哪一步失败，都再次使用原始快照尝试恢复。
            atomic_save(path, saved)
            print("回到测试前桌面：", restore_layout(path))
        with DesktopShell() as desktop:
            final = desktop.snapshot()
            if positions(final) != positions(baseline):
                raise RuntimeError("最终回退校验失败。")
        print("真实检查全部通过；原桌面坐标已精确恢复；项目 layout.json 未修改。")


if __name__ == "__main__":
    run(RUN_MOVEMENT_CHECK)

"""Windows 11 桌面 Shell 封装；仅依赖标准库，必须在同一线程内使用。

接口顺序核对自微软 win32metadata 的 ShObjIdl_core.h / ExDisp.h / servprov.h。
图标身份、枚举、读写位置全部使用 Shell COM。ListView 仅用于只读坐标校验，
不发送任何位置设置消息，也不使用控件索引作为持久化身份。
"""

import ctypes as C
import os
import uuid
from contextlib import contextmanager
from ctypes import wintypes as W


class ShellError(RuntimeError):
    pass


HRESULT = C.c_int32
UINT = C.c_uint32
LONG = C.c_int32
PTR = C.c_void_p
PPTR = C.POINTER(PTR)


class GUID(C.Structure):
    _fields_ = [("data1", UINT), ("data2", C.c_uint16), ("data3", C.c_uint16), ("data4", C.c_ubyte * 8)]

    def __init__(self, text):
        super().__init__()
        C.memmove(C.byref(self), uuid.UUID(text).bytes_le, 16)


# VARIANT 在 x64 上为 24 字节：8 字节标签 + 最大 16 字节的 union。
# 本程序仅传 VT_I4 / VT_EMPTY，没有 BSTR 或接口引用需要 VariantClear。
class VariantData(C.Union):
    _fields_ = [("lVal", LONG), ("record", PTR * 2), ("align", C.c_int64)]


class VARIANT(C.Structure):
    _anonymous_ = ("data",)
    _fields_ = [("vt", C.c_uint16), ("reserved", C.c_uint16 * 3), ("data", VariantData)]


class StrretData(C.Union):
    _fields_ = [("pOleStr", PTR), ("uOffset", UINT), ("cStr", C.c_char * 260)]


class STRRET(C.Structure):
    _anonymous_ = ("data",)
    _fields_ = [("uType", UINT), ("data", StrretData)]


class MONITORINFOEX(C.Structure):
    _fields_ = [("cbSize", UINT), ("rcMonitor", W.RECT), ("rcWork", W.RECT), ("dwFlags", UINT), ("szDevice", C.c_wchar * 32)]


class DISPLAY_DEVICE(C.Structure):
    _fields_ = [
        ("cb", UINT),
        ("DeviceName", C.c_wchar * 32),
        ("DeviceString", C.c_wchar * 128),
        ("StateFlags", UINT),
        ("DeviceID", C.c_wchar * 128),
        ("DeviceKey", C.c_wchar * 128),
    ]


IID_FOLDER_VIEW = GUID("cde725b0-ccc9-4519-917e-325d72fab4ce")
IID_FOLDER_VIEW2 = GUID("1af3a467-214f-4298-908e-06b03e0b39f9")
IID_SHELL_FOLDER = GUID("000214e6-0000-0000-c000-000000000046")
IID_ENUM_IDLIST = GUID("000214f2-0000-0000-c000-000000000046")
IID_SERVICE = GUID("6d5140c1-7436-11ce-8034-00aa006009fa")
IID_BROWSER = GUID("000214e2-0000-0000-c000-000000000046")
SID_BROWSER = GUID("4c96be40-915c-11cf-99d3-00aa004ae837")
CLSID_WINDOWS = GUID("9ba05972-f6a8-11cf-a442-00a0c90a8f39")
IID_WINDOWS = GUID("85cb6900-4d95-11cf-960c-0080c7f4ee85")


def check(hr, operation):
    if hr < 0:
        raise ShellError(f"{operation}失败（HRESULT 0x{hr & 0xFFFFFFFF:08X}）。")
    return hr


def bind(dll, name, result, args):
    function = getattr(dll, name)
    function.restype, function.argtypes = result, args
    return function


def call(pointer, slot, args=(), values=(), result=HRESULT):
    if not pointer:
        raise ShellError("Shell 返回了空 COM 接口。")
    table = C.cast(pointer, C.POINTER(C.POINTER(PTR))).contents
    method = C.WINFUNCTYPE(result, PTR, *args)(table[slot])
    return method(pointer, *values)


def release(pointer):
    if pointer:
        call(pointer, 2, result=UINT)


def query(pointer, iid):
    out = PTR()
    check(call(pointer, 0, (C.POINTER(GUID), PPTR), (C.byref(iid), C.byref(out))), "QueryInterface")
    if not out:
        raise ShellError("Shell 未返回请求的接口。")
    return out


def rect_list(rect):
    return [rect.left, rect.top, rect.right, rect.bottom]


class DesktopShell:
    """一次保存/恢复使用一个上下文，退出时释放 PIDL、接口和 COM apartment。"""

    def __init__(self):
        if os.name != "nt" or C.sizeof(PTR) != 8:
            raise ShellError("请使用 Windows 11 的 64 位 Python 3.11 或更高版本。")
        self.interfaces, self.pidls = [], {}
        self.initialized = False
        self.ole = C.WinDLL("ole32", use_last_error=True)
        self.user = C.WinDLL("user32", use_last_error=True)
        self.kernel = C.WinDLL("kernel32", use_last_error=True)
        self.shlwapi = C.WinDLL("shlwapi", use_last_error=True)
        bind(self.ole, "CoInitializeEx", HRESULT, [PTR, UINT])
        bind(self.ole, "CoUninitialize", None, [])
        bind(self.ole, "CoCreateInstance", HRESULT, [C.POINTER(GUID), PTR, UINT, C.POINTER(GUID), PPTR])
        bind(self.ole, "CoTaskMemFree", None, [PTR])
        bind(self.shlwapi, "StrRetToStrW", HRESULT, [C.POINTER(STRRET), PTR, PPTR])
        bind(self.user, "ClientToScreen", W.BOOL, [W.HWND, C.POINTER(W.POINT)])
        bind(self.user, "FindWindowExW", W.HWND, [W.HWND, W.HWND, W.LPCWSTR, W.LPCWSTR])
        bind(self.user, "GetDpiForWindow", UINT, [W.HWND])
        bind(self.user, "GetWindowThreadProcessId", UINT, [W.HWND, C.POINTER(UINT)])
        bind(self.user, "SendMessageTimeoutW", C.c_ssize_t, [W.HWND, UINT, C.c_size_t, C.c_ssize_t, UINT, UINT, C.POINTER(C.c_size_t)])
        bind(self.user, "GetMonitorInfoW", W.BOOL, [W.HMONITOR, C.POINTER(MONITORINFOEX)])
        bind(self.user, "EnumDisplayDevicesW", W.BOOL, [W.LPCWSTR, UINT, C.POINTER(DISPLAY_DEVICE), UINT])
        bind(self.user, "GetClientRect", W.BOOL, [W.HWND, C.POINTER(W.RECT)])
        bind(self.kernel, "OpenProcess", W.HANDLE, [UINT, W.BOOL, UINT])
        bind(self.kernel, "CloseHandle", W.BOOL, [W.HANDLE])
        bind(self.kernel, "VirtualAllocEx", PTR, [W.HANDLE, PTR, C.c_size_t, UINT, UINT])
        bind(self.kernel, "VirtualFreeEx", W.BOOL, [W.HANDLE, PTR, C.c_size_t, UINT])
        for name in ("ReadProcessMemory", "WriteProcessMemory"):
            bind(self.kernel, name, W.BOOL, [W.HANDLE, PTR, PTR, C.c_size_t, C.POINTER(C.c_size_t)])

    def keep(self, pointer):
        if not pointer:
            raise ShellError("Shell COM 接口为空。")
        self.interfaces.append(pointer)
        return pointer

    def __enter__(self):
        try:
            # S_OK 和 S_FALSE 都必须配对 CoUninitialize；RPC_E_CHANGED_MODE 则不能。
            check(self.ole.CoInitializeEx(None, 2), "初始化 COM STA")
            self.initialized = True
            windows = PTR()
            check(self.ole.CoCreateInstance(C.byref(CLSID_WINDOWS), None, 0x15, C.byref(IID_WINDOWS), C.byref(windows)), "连接桌面 Shell")
            self.keep(windows)
            location, empty = VARIANT(), VARIANT()
            location.vt, location.lVal = 3, 0  # VT_I4 / CSIDL_DESKTOP
            hwnd32, dispatch = LONG(), PTR()
            check(
                call(
                    windows,
                    15,
                    (C.POINTER(VARIANT), C.POINTER(VARIANT), C.c_int, C.POINTER(LONG), C.c_int, PPTR),
                    (C.byref(location), C.byref(empty), 8, C.byref(hwnd32), 1, C.byref(dispatch)),
                ),
                "定位桌面 Shell View",
            )
            self.keep(dispatch)
            service = self.keep(query(dispatch, IID_SERVICE))
            browser = PTR()
            check(
                call(service, 3, (C.POINTER(GUID), C.POINTER(GUID), PPTR), (C.byref(SID_BROWSER), C.byref(IID_BROWSER), C.byref(browser))),
                "取得桌面 IShellBrowser",
            )
            self.keep(browser)
            self.view = PTR()
            check(call(browser, 15, (PPTR,), (C.byref(self.view),)), "取得 IShellView")
            self.keep(self.view)
            self.folder_view = self.keep(query(self.view, IID_FOLDER_VIEW))
            self.folder_view2 = self.keep(query(self.view, IID_FOLDER_VIEW2))
            self.folder = PTR()
            check(call(self.folder_view, 5, (C.POINTER(GUID), PPTR), (C.byref(IID_SHELL_FOLDER), C.byref(self.folder))), "取得桌面 IShellFolder")
            self.keep(self.folder)
            self.hwnd = W.HWND()
            check(call(self.view, 3, (C.POINTER(W.HWND),), (C.byref(self.hwnd),)), "读取 Shell View 窗口")
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        self.free_pidls()
        for pointer in reversed(self.interfaces):
            release(pointer)
        self.interfaces.clear()
        if self.initialized:
            self.ole.CoUninitialize()
            self.initialized = False

    def free_pidls(self):
        for pidl in self.pidls.values():
            self.ole.CoTaskMemFree(pidl)
        self.pidls.clear()

    def name(self, pidl, flags):
        value, text = STRRET(), PTR()
        check(call(self.folder, 11, (PTR, UINT, C.POINTER(STRRET)), (pidl, flags, C.byref(value))), "读取图标身份或名称")
        # StrRetToStrW 消费 STRRET_WSTR，并返回另一个 CoTaskMemAlloc 字符串。
        check(self.shlwapi.StrRetToStrW(C.byref(value), pidl, C.byref(text)), "转换图标名称")
        try:
            return C.wstring_at(text) if text else ""
        finally:
            self.ole.CoTaskMemFree(text)

    def position(self, pidl):
        point = W.POINT()
        check(call(self.folder_view, 11, (PTR, C.POINTER(W.POINT)), (pidl, C.byref(point))), "读取图标位置")
        return [point.x, point.y]

    def enumerate_icons(self):
        self.free_pidls()
        enum = PTR()
        check(call(self.folder_view, 8, (UINT, C.POINTER(GUID), PPTR), (2, C.byref(IID_ENUM_IDLIST), C.byref(enum))), "枚举桌面图标")
        icons = []
        try:
            while True:
                pidl, fetched = PTR(), UINT()
                hr = call(enum, 3, (UINT, PPTR, C.POINTER(UINT)), (1, C.byref(pidl), C.byref(fetched)))
                try:
                    check(hr, "读取桌面枚举项")
                    if hr == 1 and fetched.value == 0:
                        break
                    if hr != 0 or fetched.value != 1 or not pidl:
                        raise ShellError("桌面枚举结果不完整，请等待 Explorer 稳定后重试。")
                    identity = self.name(pidl, 0x8000)  # SHGDN_FORPARSING，不解析 .lnk 目标
                    if not identity or identity in self.pidls:
                        raise ShellError(f"图标身份为空或发生冲突：{identity!r}；已停止操作。")
                    icons.append({"id": identity, "name": self.name(pidl, 0), "position": self.position(pidl)})
                    self.pidls[identity] = pidl
                    pidl = None  # 所有权转交给会话，移动时使用当前 PIDL
                finally:
                    if pidl:
                        self.ole.CoTaskMemFree(pidl)
        finally:
            release(enum)
        count = C.c_int()
        check(call(self.folder_view, 7, (UINT, C.POINTER(C.c_int)), (2, C.byref(count))), "核对图标数量")
        if count.value != len(icons):
            raise ShellError("读取期间桌面图标发生变化，请重试。")
        return icons

    def auto_arrange(self):
        hr = check(call(self.folder_view, 14), "读取自动排列状态")
        if hr not in (0, 1):
            raise ShellError("无法确定自动排列状态。")
        return hr == 0  # S_FALSE 明确表示关闭，不是错误。

    def monitors(self):
        monitors, errors = [], []
        callback_type = C.WINFUNCTYPE(W.BOOL, W.HMONITOR, W.HDC, C.POINTER(W.RECT), C.c_ssize_t)

        def collect(handle, _dc, _rect, _data):
            try:
                info = MONITORINFOEX()
                info.cbSize = C.sizeof(info)
                if not self.user.GetMonitorInfoW(handle, C.byref(info)):
                    raise C.WinError(C.get_last_error())
                ids = []
                index = 0
                while True:
                    device = DISPLAY_DEVICE()
                    device.cb = C.sizeof(device)
                    if not self.user.EnumDisplayDevicesW(info.szDevice, index, C.byref(device), 1):
                        break
                    if device.StateFlags & 1 and device.DeviceID:
                        ids.append(device.DeviceID)
                    index += 1
                # 设备接口路径比 DISPLAY1/2 稳定；缺失或克隆模式时不假装可靠匹配。
                monitors.append(
                    {
                        "key": info.szDevice,
                        "device_id": ids[0] if len(ids) == 1 else None,
                        "rect": rect_list(info.rcMonitor),
                        "work": rect_list(info.rcWork),
                        "primary": bool(info.dwFlags & 1),
                    }
                )
                # 缩放只是适配元数据，读取失败不阻止单屏布局迁移。
                scale = UINT()
                try:
                    get_scale = bind(C.WinDLL("shcore"), "GetScaleFactorForMonitor", HRESULT, [W.HMONITOR, C.POINTER(UINT)])
                    monitors[-1]["scale"] = scale.value if get_scale(handle, C.byref(scale)) == 0 else None
                except OSError:
                    monitors[-1]["scale"] = None
                return True
            except Exception as error:
                errors.append(error)
                return False

        callback = callback_type(collect)
        enum = bind(self.user, "EnumDisplayMonitors", W.BOOL, [W.HDC, C.POINTER(W.RECT), callback_type, C.c_ssize_t])
        if not enum(None, None, callback, 0) or errors:
            raise ShellError(f"读取显示器工作区失败：{errors[0] if errors else C.WinError()}")
        if sum(m["primary"] for m in monitors) != 1:
            raise ShellError("无法唯一识别当前 Windows 主显示器。")
        return sorted(monitors, key=lambda m: (not m["primary"], m["key"]))

    @contextmanager
    def geometry_buffer(self, hwnd):
        """只读 GET 消息需在 Explorer 地址空间接收 POINT/RECT，不能传本进程指针。

        仅分配自己的 16 字节缓冲区；不改 Explorer 数据或图标位置。
        SendMessageTimeout 防止界面挂起。若超时，不释放可能仍被消息使用的缓冲区，
        最多留下 16 字节，由 Explorer 退出时回收，避免 use-after-free。
        """
        pid = UINT()
        if not self.user.GetWindowThreadProcessId(hwnd, C.byref(pid)):
            raise ShellError("桌面窗口已经失效。")
        process = self.kernel.OpenProcess(0x8 | 0x10 | 0x20, False, pid.value)
        if not process:
            raise ShellError("无法读取桌面坐标校验信息，请以普通用户运行并检查 Explorer。")
        memory, timed_out = None, False
        try:
            memory = self.kernel.VirtualAllocEx(process, None, 16, 0x3000, 0x04)
            if not memory:
                raise C.WinError(C.get_last_error())

            def read(message, index, structure):
                nonlocal timed_out
                size = C.sizeof(structure)
                transferred = C.c_size_t()
                if not self.kernel.WriteProcessMemory(process, memory, C.byref(structure), size, C.byref(transferred)) or transferred.value != size:
                    raise ShellError("初始化只读坐标缓冲区失败。")
                result = C.c_size_t()
                if not self.user.SendMessageTimeoutW(hwnd, message, index, memory, 0x22, 2000, C.byref(result)):
                    timed_out = True
                    raise ShellError("桌面坐标查询超时或窗口失效，请稍后重试。")
                if not result.value:
                    raise ShellError("桌面控件不支持所需的只读坐标查询。")
                if not self.kernel.ReadProcessMemory(process, memory, C.byref(structure), size, C.byref(transferred)) or transferred.value != size:
                    raise ShellError("读取坐标校验结果失败。")
                return structure

            yield read
        finally:
            if memory and not timed_out:
                self.kernel.VirtualFreeEx(process, memory, 0, 0x8000)
            self.kernel.CloseHandle(process)

    def geometry(self, icons):
        """验证 Shell 坐标与控件 view 坐标一致，再通过窗口原点和滚动原点转换。

        screen = shell_position - scroll_origin + ClientToScreen(0, 0)。
        不假设 Shell 原点等于主屏原点，也不假设虚拟桌面左上角为 (0, 0)。
        """
        hwnd = self.user.FindWindowExW(self.hwnd, None, "SysListView32", None)
        if not hwnd:
            raise ShellError("无法校验桌面视图坐标：未找到标准桌面图标视图；未移动任何图标。")
        spacing, mode, size, flags = W.POINT(), UINT(), C.c_int(), UINT()
        check(call(self.folder_view, 12, (C.POINTER(W.POINT),), (C.byref(spacing),)), "读取网格间距")
        check(call(self.folder_view2, 36, (C.POINTER(UINT), C.POINTER(C.c_int)), (C.byref(mode), C.byref(size))), "读取图标大小")
        check(call(self.folder_view2, 25, (C.POINTER(UINT),), (C.byref(flags),)), "读取视图选项")
        if spacing.x <= 0 or spacing.y <= 0 or size.value <= 0 or mode.value not in (1, 5):
            raise ShellError("当前桌面不是支持的图标视图，或网格间距无效。")
        origin = W.POINT()
        if not self.user.ClientToScreen(hwnd, C.byref(origin)):
            raise C.WinError(C.get_last_error())
        bounds = None
        with self.geometry_buffer(hwnd) as read:
            scroll = read(0x1029, 0, W.POINT())  # LVM_GETORIGIN
            origin.x -= scroll.x
            origin.y -= scroll.y
            # 检查每一项，避免仅一个短名称的矩形遗漏长名称占用的空间。
            for index in range(len(icons)):
                pidl = PTR()
                check(call(self.folder_view, 6, (C.c_int, PPTR), (index, C.byref(pidl))), "读取校验图标")
                try:
                    shell_point = self.position(pidl)
                    point = read(0x1010, index, W.POINT())  # LVM_GETITEMPOSITION，只读
                    if shell_point != [point.x, point.y]:
                        raise ShellError("Shell 与视图控件的坐标不一致；为防止错位已停止操作。")
                    rect = read(0x100E, index, W.RECT())  # LVIR_BOUNDS = 0，返回 client 坐标
                    item_bounds = [
                        rect.left + scroll.x - point.x,
                        rect.top + scroll.y - point.y,
                        rect.right + scroll.x - point.x,
                        rect.bottom + scroll.y - point.y,
                    ]
                    if bounds is None:
                        bounds = item_bounds
                    else:
                        bounds = [
                            min(bounds[0], item_bounds[0]),
                            min(bounds[1], item_bounds[1]),
                            max(bounds[2], item_bounds[2]),
                            max(bounds[3], item_bounds[3]),
                        ]
                finally:
                    self.ole.CoTaskMemFree(pidl)
        # 没有图标时无法抽样验证；没有任何旧位置需要转换，网格从完整 cell 左上角开始。
        if bounds is None:
            bounds = [0, 0, spacing.x, spacing.y]
        return {
            "origin": [origin.x, origin.y],
            "spacing": [spacing.x, spacing.y],
            "icon_size": size.value,
            "dpi": self.user.GetDpiForWindow(hwnd),
            "bounds": bounds,
            "snap_to_grid": bool(flags.value & 0x4),
            "coordinate_system": "shell-view-physical-v1",
        }

    def snapshot(self):
        icons = self.enumerate_icons()
        return {"icons": icons, "view": self.geometry(icons), "monitors": self.monitors(), "auto_arrange": self.auto_arrange()}

    def move(self, positions):
        """positions: 身份 -> Shell view POINT；整批提交，PIDL 只在本会话有效。"""
        if self.auto_arrange():
            raise ShellError("桌面已开启“自动排列图标”，请在桌面右键 → 查看中手动关闭后重试。")
        if not positions:
            return
        if not set(positions) <= self.pidls.keys():
            raise ShellError("桌面图标已经变化，请重新读取后恢复。")
        count = len(positions)
        pidls = (PTR * count)(*(self.pidls[key].value for key in positions))
        points = (W.POINT * count)(*(W.POINT(*point) for point in positions.values()))
        check(
            call(self.folder_view, 16, (UINT, C.POINTER(PTR), C.POINTER(W.POINT), UINT), (count, pidls, points, 0x80)), "批量恢复图标位置"
        )  # SVSI_POSITIONITEM


def enable_dpi_awareness():
    """在创建 Tk 窗口之前设置 PMv2，确保显示器和 ClientToScreen 使用物理像素。"""
    if os.name != "nt":
        raise ShellError("此程序只能在 Windows 11 的桌面会话中运行。")
    user = C.WinDLL("user32", use_last_error=True)
    set_process = bind(user, "SetProcessDpiAwarenessContext", W.BOOL, [PTR])
    set_thread = bind(user, "SetThreadDpiAwarenessContext", PTR, [PTR])
    set_process(PTR(-4))  # 宿主可能已设置进程模式，下面显式确保当前线程为 PMv2。
    if not set_thread(PTR(-4)):
        raise ShellError("无法启用 Per-Monitor V2 DPI 坐标模式。")

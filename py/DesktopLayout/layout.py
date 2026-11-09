"""不依赖 Windows 的布局计算、JSON 校验与原子保存，便于真实的单元测试。"""

import json
import math
import os
import re
import tempfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path

VERSION = 1
COORDINATES = "shell-view-physical-v1"


class LayoutError(ValueError):
    pass


def natural_key(icon):
    # 数字和文本分别标记类型，避免 Python 3 比较 int / str；身份作稳定的最终平局键。
    parts = re.split(r"(\d+)", icon["name"].casefold())
    return ([(1, int(p)) if p.isdecimal() else (0, p) for p in parts], icon["id"])


def unique_icons(icons):
    result = {}
    for icon in icons:
        identity = icon["id"]
        if identity in result:
            raise LayoutError(f"图标身份冲突：{identity}。未执行恢复。")
        result[identity] = icon
    return result


def screen_point(position, view):
    return [position[k] + view["origin"][k] for k in (0, 1)]


def shell_point(position, view):
    return [position[k] - view["origin"][k] for k in (0, 1)]


def contains(rect, point):
    return rect[0] <= point[0] < rect[2] and rect[1] <= point[1] < rect[3]


def icon_box(point, view):
    b = view["bounds"]
    return [point[0] + b[0], point[1] + b[1], point[0] + b[2], point[1] + b[3]]


def overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def fits(point, monitor, view):
    b, w = icon_box(point, view), monitor["work"]
    return w[0] <= b[0] and w[1] <= b[1] and b[2] <= w[2] and b[3] <= w[3]


def grid(monitor, view):
    """返回当前工作区首个完整网格锚点及容量。

    Windows 图标位置是图像锚点，并非整个图标/文字 cell 的左上角。
    从只读测得的左边界偏移确定横向相位；纵向相位以视图原点为基准。
    通过 ceil 跳过任务栏/屏幕外的行列，不从当前最左图标推断原点，避免累计漂移。
    """
    work, bounds, spacing = monitor["work"], view["bounds"], view["spacing"]
    phase = [view["origin"][0] - bounds[0], view["origin"][1]]
    first, count = [], []
    for axis in (0, 1):
        start = phase[axis] + math.ceil((work[axis] - bounds[axis] - phase[axis]) / spacing[axis]) * spacing[axis]
        first.append(start)
        count.append(max(0, (work[axis + 2] - bounds[axis + 2] - start) // spacing[axis] + 1))
    if count[0] * count[1] > 200_000:
        raise LayoutError("显示器网格容量异常，无法可靠计算布局。")
    return first, count


def grid_position(monitor, view, cell):
    start, _ = grid(monitor, view)
    return [start[k] + cell[k] * view["spacing"][k] for k in (0, 1)]


def grid_cell(point, monitor, view):
    start, _ = grid(monitor, view)
    return [math.floor((point[k] - start[k]) / view["spacing"][k] + 0.5) for k in (0, 1)]


def cells(monitor, view):
    start, count = grid(monitor, view)
    for column in range(count[0]):
        for row in range(count[1]):
            yield [start[0] + column * view["spacing"][0], start[1] + row * view["spacing"][1]]


def validate_state(state):
    """所有外部 JSON 必须先校验，再进入位置算法；bool 不能冒充 int。"""

    def fail():
        raise LayoutError("布局数据格式无效或必要字段不一致，请重新保存布局。")

    def integers(value, size):
        if not isinstance(value, list) or len(value) != size:
            fail()
        if any(type(n) is not int or abs(n) > 1_000_000 for n in value):
            fail()

    def rectangle(value):
        integers(value, 4)
        if value[0] >= value[2] or value[1] >= value[3]:
            fail()

    try:
        view = state["view"]
        if view["coordinate_system"] != COORDINATES:
            fail()
        for key in ("origin", "spacing"):
            integers(view[key], 2)
        if not all(8 <= n <= 4096 for n in view["spacing"]):
            fail()
        rectangle(view["bounds"])
        for key in ("icon_size", "dpi"):
            if type(view[key]) is not int or not 1 <= view[key] <= 4096:
                fail()
        if type(view["snap_to_grid"]) is not bool or type(state["auto_arrange"]) is not bool:
            fail()
        monitors = state["monitors"]
        if not isinstance(monitors, list) or not 1 <= len(monitors) <= 64:
            fail()
        keys = set()
        for monitor in monitors:
            if not isinstance(monitor["key"], str) or not monitor["key"] or monitor["key"] in keys:
                fail()
            keys.add(monitor["key"])
            device = monitor["device_id"]
            if device is not None and (not isinstance(device, str) or not device):
                fail()
            if type(monitor["primary"]) is not bool:
                fail()
            scale = monitor.get("scale")
            if scale is not None and (type(scale) is not int or not 50 <= scale <= 1000):
                fail()
            rectangle(monitor["rect"])
            rectangle(monitor["work"])
            r, w = monitor["rect"], monitor["work"]
            if w[0] < r[0] or w[1] < r[1] or w[2] > r[2] or w[3] > r[3]:
                fail()
        if sum(m["primary"] for m in monitors) != 1:
            fail()
        for i, a in enumerate(monitors):
            if any(overlaps(a["rect"], b["rect"]) for b in monitors[i + 1 :]):
                raise LayoutError("当前显示区域重叠；请使用扩展桌面模式。")
        icons = state["icons"]
        if not isinstance(icons, list) or len(icons) > 10000:
            fail()
        for icon in icons:
            if not isinstance(icon["id"], str) or not icon["id"] or not isinstance(icon["name"], str):
                fail()
            integers(icon["position"], 2)
        unique_icons(icons)
    except (KeyError, TypeError, IndexError, AttributeError):
        fail()


def validate_layout(data):
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != VERSION:
        raise LayoutError("不支持的布局版本或布局文件损坏，请重新保存。")
    validate_state(data)
    try:
        if not isinstance(data["saved_at"], str) or datetime.fromisoformat(data["saved_at"]).tzinfo is None:
            raise ValueError
        if type(data["monitor_count"]) is not int or data["monitor_count"] != len(data["monitors"]):
            raise ValueError
        monitors = {m["key"]: m for m in data["monitors"]}
        for icon in data["icons"]:
            monitor = monitors[icon["monitor"]]
            point = screen_point(icon["position"], data["view"])
            local = [point[k] - monitor["rect"][k] for k in (0, 1)]
            for field in ("local", "grid"):
                value = icon[field]
                if not isinstance(value, list) or len(value) != 2 or any(type(n) is not int for n in value):
                    raise ValueError
            if not contains(monitor["rect"], point) or icon["local"] != local:
                raise ValueError
            if icon["grid"] != grid_cell(point, monitor, data["view"]):
                raise ValueError
    except (KeyError, TypeError, ValueError, IndexError):
        raise LayoutError("保存时间、显示器归属或图标坐标数据损坏，请重新保存布局。") from None
    return data


def make_layout(state):
    validate_state(state)
    data = deepcopy(state)
    data.update(version=VERSION, saved_at=datetime.now().astimezone().isoformat(timespec="seconds"), monitor_count=len(state["monitors"]))
    for icon in data["icons"]:
        point = screen_point(icon["position"], state["view"])
        matches = [m for m in state["monitors"] if contains(m["rect"], point)]
        if len(matches) != 1:
            raise LayoutError(f"无法确定图标“{icon['name']}”所在显示器，请先将它放回可见桌面。")
        monitor = matches[0]
        icon.update(monitor=monitor["key"], local=[point[k] - monitor["rect"][k] for k in (0, 1)], grid=grid_cell(point, monitor, state["view"]))
    return validate_layout(data)


def atomic_save(path, data):
    validate_layout(data)
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, prefix=".layout-", suffix=".tmp", delete=False
        ) as file:
            temporary = Path(file.name)
            json.dump(data, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)  # 同目录/同卷替换，失败时保留旧文件。
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_layout(path):
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise LayoutError(f"JSON 字段重复：{key}。")
            result[key] = value
        return result

    try:
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file, object_pairs_hook=no_duplicates)
    except FileNotFoundError:
        raise LayoutError("尚未保存布局，请先点击“保存布局”。") from None
    except (json.JSONDecodeError, UnicodeError, RecursionError):
        raise LayoutError("layout.json 已损坏或不是有效 UTF-8 JSON；未移动图标。") from None
    return validate_layout(data)


def environment_signature(monitor, view):
    rect = monitor["rect"]
    first, _ = grid(monitor, view)
    return (
        tuple(view["spacing"]),
        view["icon_size"],
        view["dpi"],
        monitor.get("scale"),
        view["snap_to_grid"],
        tuple(view["bounds"][:2]),
        (rect[2] - rect[0], rect[3] - rect[1]),
        tuple(monitor["work"][k] - rect[k % 2] for k in range(4)),
        tuple(first[k] - rect[k] for k in (0, 1)),
    )


def plan_restore(saved, current):
    """先计算整批计划，绝不在搜索位置时移动图标。所有占用判断均用屏幕物理坐标。"""
    validate_layout(saved)
    validate_state(current)
    if current["auto_arrange"]:
        raise LayoutError("桌面已开启“自动排列图标”，请在桌面右键 → 查看中手动关闭后重试。")
    old, now = unique_icons(saved["icons"]), unique_icons(current["icons"])
    old_monitors = {m["key"]: m for m in saved["monitors"]}
    monitors = sorted(current["monitors"], key=lambda m: (not m["primary"], m["key"]))
    used = {i["monitor"] for i in saved["icons"]}
    single = len(used) <= 1  # 依据图标分布，不依据连接的显示器数量。
    mapping, notes = {}, []
    if single:
        mapping = {key: monitors[0] for key in used}
    else:
        for key in sorted(used):
            device = old_monitors[key]["device_id"]
            matches = [m for m in monitors if device and m["device_id"] and m["device_id"].casefold() == device.casefold()]
            old_matches = [m for m in saved["monitors"] if device and m["device_id"] and m["device_id"].casefold() == device.casefold()]
            if len(matches) == 1 and len(old_matches) == 1:
                mapping[key] = matches[0]
            elif any(i["monitor"] == key and i["id"] in now for i in saved["icons"]):
                raise LayoutError(f"跨屏布局无法可靠匹配显示器 {key}，且该屏仍有图标需要恢复；未移动任何图标。")
            else:
                notes.append(f"显示器 {key} 无法匹配且其旧图标均已缺失，忽略该屏保留位。")

    view = current["view"]
    placed, reserved, targets = {}, {}, {}

    def desired(icon):
        monitor = mapping.get(icon["monitor"])
        if monitor is None:
            return None, None
        source = old_monitors[icon["monitor"]]
        if environment_signature(source, saved["view"]) == environment_signature(monitor, view):
            point = [monitor["rect"][k] + icon["local"][k] for k in (0, 1)]
        else:
            point = grid_position(monitor, view, icon["grid"])
        return monitor, point

    def conflict(point, boxes):
        box = icon_box(point, view)
        return any(overlaps(box, b) for b in boxes.values())

    def assign(identity, point):
        placed[identity] = icon_box(point, view)
        targets[identity] = shell_point(point, view)

    ordered = sorted(saved["icons"], key=lambda i: (i["monitor"], i["grid"][0], i["grid"][1], natural_key(i)))
    overflow = []
    for icon in ordered:
        if icon["id"] not in now:
            continue
        monitor, point = desired(icon)
        if fits(point, monitor, view) and not conflict(point, placed):
            assign(icon["id"], point)
        else:
            overflow.append((icon, monitor))

    for icon in ordered:
        if icon["id"] in now:
            continue
        monitor, point = desired(icon)
        if monitor and fits(point, monitor, view) and not conflict(point, placed):
            reserved[icon["id"]] = icon_box(point, view)

    released = set()

    def allocate(icon, destinations):
        # 先搜索所有可用屏的非保留空格；确实放不下时才释放被删除图标的空位。
        for allow_reserved in (False, True):
            for monitor in destinations:
                for point in cells(monitor, view):
                    if conflict(point, placed) or (not allow_reserved and conflict(point, reserved)):
                        continue
                    if allow_reserved:
                        box = icon_box(point, view)
                        for identity in list(reserved):
                            if overlaps(box, reserved[identity]):
                                released.add(identity)
                                del reserved[identity]
                    assign(icon["id"], point)
                    return
        raise LayoutError(f"可用网格不足，无法放置“{icon['name']}”；未移动任何图标。")

    for icon, monitor in overflow:
        allocate(icon, monitors if single else [monitor])
    added = sorted((i for key, i in now.items() if key not in old), key=natural_key)
    for icon in added:
        allocate(icon, monitors)
    if overflow:
        notes.append(f"{len(overflow)} 个旧位置越界或冲突，已重新分配。")
    if released:
        notes.append(f"容量不足，释放了 {len(released)} 个缺失图标保留位。")
    return {
        "positions": targets,
        "existing": len(old.keys() & now.keys()),
        "missing": len(old.keys() - now.keys()),
        "added": len(added),
        "reserved": len(reserved),
        "released": len(released),
        "single_screen": single,
        "notes": notes,
    }


def verify_positions(state, targets, tolerance=0, check_geometry=True):
    """容差只用于比较目标与回读位置；不允许用容差掩盖重叠或越界。"""
    actual = unique_icons(state["icons"])
    errors, boxes = [], []
    if actual.keys() != targets.keys():
        errors.append("恢复期间图标集合发生变化")
    for identity, target in targets.items():
        icon = actual.get(identity)
        if icon is None:
            errors.append(f"图标已消失：{identity}")
        elif any(abs(icon["position"][k] - target[k]) > tolerance for k in (0, 1)):
            errors.append(f"位置未达到目标：{icon['name']}")
    if check_geometry:
        for icon in state["icons"]:
            point = screen_point(icon["position"], state["view"])
            if not any(fits(point, m, state["view"]) for m in state["monitors"]):
                errors.append(f"图标越界：{icon['name']}")
            box = icon_box(point, state["view"])
            if any(overlaps(box, old_box) for old_box in boxes):
                errors.append(f"图标重叠：{icon['name']}")
            boxes.append(box)
    return errors

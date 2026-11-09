"""纯算法及事务模拟测试，不连接或移动真实 Windows 桌面。"""

import ctypes
import random
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from layout import (
    LayoutError,
    atomic_save,
    grid_position,
    load_layout,
    make_layout,
    plan_restore,
    shell_point,
    validate_layout,
    verify_positions,
)
from main import positions, restore_layout, save_layout
from shell_api import GUID, STRRET, VARIANT, ShellError, check


def monitor(key="a", x=0, y=0, width=400, height=400, primary=True, device=None):
    return {
        "key": key,
        "device_id": device or "physical-" + key,
        "rect": [x, y, x + width, y + height],
        "work": [x, y, x + width, y + height],
        "primary": primary,
        "scale": 100,
    }


def state(monitors=None, specs=(), spacing=(100, 100), origin=(0, 0)):
    result = {
        "monitors": monitors or [monitor()],
        "icons": [],
        "auto_arrange": False,
        "view": {
            "origin": list(origin),
            "spacing": list(spacing),
            "icon_size": 48,
            "dpi": 96,
            "bounds": [0, 0, 80, 80],
            "snap_to_grid": True,
            "coordinate_system": "shell-view-physical-v1",
        },
    }
    for identity, name, display, col, row in specs:
        m = next(m for m in result["monitors"] if m["key"] == display)
        point = grid_position(m, result["view"], [col, row])
        result["icons"].append({"id": identity, "name": name, "position": shell_point(point, result["view"])})
    return result


def apply_plan(current, plan):
    result = deepcopy(current)
    for icon in result["icons"]:
        icon["position"] = list(plan["positions"][icon["id"]])
    return result


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.base = state(specs=[("file-a", "A", "a", 1, 1), ("file-b", "B", "a", 2, 2)])
        self.saved = make_layout(self.base)

    def assert_valid(self, current, plan):
        self.assertEqual(verify_positions(apply_plan(current, plan), plan["positions"]), [])

    def test_exact_coordinates_even_off_grid(self):
        self.base["icons"][0]["position"] = [112, 108]
        saved = make_layout(self.base)
        plan = plan_restore(saved, self.base)
        self.assertEqual(plan["positions"], positions(self.base))

    def test_missing_reservation_and_natural_column_order(self):
        saved = make_layout(state(specs=[("gone", "Gone", "a", 0, 0), ("old", "Old", "a", 1, 1)]))
        current = state(specs=[("old", "Old", "a", 3, 0), ("new10", "文件10", "a", 3, 1), ("new2", "文件2", "a", 3, 2), ("new1", "文件1", "a", 3, 3)])
        plan = plan_restore(saved, current)
        self.assertEqual(plan["positions"]["old"], [100, 100])
        self.assertEqual([plan["positions"][k] for k in ("new1", "new2", "new10")], [[0, 100], [0, 200], [0, 300]])
        self.assertEqual(plan["reserved"], 1)
        self.assert_valid(current, plan)

    def test_deleted_only(self):
        current = deepcopy(self.base)
        current["icons"].pop()
        plan = plan_restore(self.saved, current)
        self.assertEqual((plan["missing"], plan["reserved"], plan["added"]), (1, 1, 0))

    def test_save_again_discards_missing_reservation(self):
        current = state(specs=[("file-a", "A", "a", 1, 1)])
        saved = make_layout(current)
        current["icons"].append({"id": "new", "name": "New", "position": [300, 300]})
        plan = plan_restore(saved, current)
        self.assertEqual(plan["missing"], 0)
        self.assertEqual(plan["positions"]["new"], [0, 0])

    def test_same_names_distinct_identities(self):
        current = state(specs=[("C:\\User\\A.lnk", "A", "a", 0, 0), ("C:\\Public\\A.lnk", "A", "a", 1, 0)])
        saved = make_layout(current)
        current["icons"].reverse()
        self.assertEqual(plan_restore(saved, current)["positions"], positions(current))

    def test_identity_conflicts_rejected(self):
        for which in ("saved", "current"):
            saved, current = deepcopy(self.saved), deepcopy(self.base)
            data = saved if which == "saved" else current
            data["icons"].append(deepcopy(data["icons"][0]))
            with self.subTest(which=which), self.assertRaisesRegex(LayoutError, "身份冲突"):
                plan_restore(saved, current)

    def test_rename_is_missing_and_new(self):
        current = deepcopy(self.base)
        current["icons"][0].update(id="renamed", name="A new")
        plan = plan_restore(self.saved, current)
        self.assertEqual((plan["missing"], plan["added"], plan["reserved"]), (1, 1, 1))
        self.assertEqual(plan["positions"]["renamed"], [0, 0])

    def test_idempotent_and_input_order_independent(self):
        current = state(specs=[("file-a", "A", "a", 3, 0), ("new", "New", "a", 3, 2)])
        plan = plan_restore(self.saved, current)
        again = apply_plan(current, plan)
        again["icons"].reverse()
        self.assertEqual(plan_restore(self.saved, again), plan)
        self.assert_valid(current, plan)

    def test_grid_spacing_and_icon_size_change(self):
        current = state(specs=[("file-a", "A", "a", 0, 0), ("file-b", "B", "a", 0, 1)], spacing=(120, 110))
        current["view"]["icon_size"] = 64
        plan = plan_restore(self.saved, current)
        self.assertEqual(plan["positions"], {"file-a": [120, 110], "file-b": [240, 220]})

    def test_resolution_grows_retains_cells(self):
        current = state([monitor(width=600, height=600)], [("file-a", "A", "a", 0, 0), ("file-b", "B", "a", 0, 1)])
        self.assertEqual(plan_restore(self.saved, current)["positions"], positions(self.base))

    def test_resolution_shrinks_reallocates_overflow(self):
        current = state([monitor(width=200, height=200)], [("file-a", "A", "a", 0, 0), ("file-b", "B", "a", 0, 1)])
        plan = plan_restore(self.saved, current)
        self.assertEqual(plan["positions"]["file-a"], [100, 100])
        self.assertEqual(plan["positions"]["file-b"], [0, 0])
        self.assert_valid(current, plan)

    def test_work_area_changes_with_top_left_taskbars(self):
        current = deepcopy(self.base)
        current["monitors"][0]["work"] = [50, 40, 400, 400]
        plan = plan_restore(self.saved, current)
        self.assertEqual(plan["positions"]["file-a"], [200, 200])
        self.assert_valid(current, plan)

    def test_existing_precedes_missing_conflicting_cells(self):
        base = state(specs=[("gone", "A", "a", 0, 0), ("kept", "B", "a", 0, 0)])
        current = state(specs=[("kept", "B", "a", 2, 2)])
        plan = plan_restore(make_layout(base), current)
        self.assertEqual(plan["positions"]["kept"], [0, 0])
        self.assertEqual(plan["reserved"], 0)

    def test_existing_collision_reallocated(self):
        self.base["icons"][1]["position"] = [105, 105]
        saved = make_layout(self.base)
        plan = plan_restore(saved, self.base)
        self.assert_valid(self.base, plan)
        self.assertNotEqual(plan["positions"]["file-a"], plan["positions"]["file-b"])

    def test_reserved_cells_released_only_if_needed(self):
        small = [monitor(width=200, height=100)]
        saved = make_layout(state(small, [("gone", "A", "a", 0, 0), ("keep", "B", "a", 1, 0)]))
        current = state(small, [("keep", "B", "a", 0, 0), ("new", "C", "a", 1, 0)])
        plan = plan_restore(saved, current)
        self.assertEqual((plan["released"], plan["reserved"]), (1, 0))
        self.assertEqual(plan["positions"]["keep"], [100, 0])
        self.assert_valid(current, plan)

    def test_capacity_insufficient_rejects_whole_plan(self):
        current = state([monitor(width=100, height=100)], [("file-a", "A", "a", 0, 0), ("file-b", "B", "a", 0, 0)])
        with self.assertRaisesRegex(LayoutError, "网格不足"):
            plan_restore(self.saved, current)

    def test_single_screen_overflow_to_secondary(self):
        current = state(
            [monitor(width=100, height=100), monitor("b", 100, width=100, height=100, primary=False)],
            [("file-a", "A", "a", 0, 0), ("file-b", "B", "b", 0, 0)],
        )
        plan = plan_restore(self.saved, current)
        self.assertEqual(set(map(tuple, plan["positions"].values())), {(0, 0), (100, 0)})
        self.assert_valid(current, plan)

    def test_other_screen_before_releasing_reservations(self):
        saved = make_layout(state([monitor(width=100, height=100)], [("gone", "A", "a", 0, 0)]))
        current = state([monitor(width=100, height=100), monitor("b", 100, width=100, height=100, primary=False)], [("new", "B", "a", 0, 0)])
        plan = plan_restore(saved, current)
        self.assertEqual(plan["positions"]["new"], [100, 0])
        self.assertEqual(plan["released"], 0)

    def test_single_screen_configuration_matrix(self):
        dual = [monitor(), monitor("b", 400, primary=False)]
        saved = make_layout(state(dual, [("one", "One", "a", 1, 1)]))
        configurations = {
            "unchanged": dual,
            "only_dp": [monitor()],
            "only_hdmi": [monitor("b")],
            "three": dual + [monitor("c", -400, primary=False)],
            "new_primary": [monitor(primary=False), monitor("b", 400, primary=True)],
            "swap_sides": [monitor(x=400), monitor("b", 0, primary=False)],
            "laptop": [monitor("laptop", width=600, height=600)],
            "renumber": [monitor("changed", device="physical-a")],
        }
        for scenario, displays in configurations.items():
            with self.subTest(scenario=scenario):
                primary = next(m for m in displays if m["primary"])
                current = state(displays, [("one", "One", primary["key"], 0, 0)])
                plan = plan_restore(saved, current)
                expected = grid_position(primary, current["view"], [1, 1])
                self.assertTrue(plan["single_screen"])
                self.assertEqual(plan["positions"]["one"], shell_point(expected, current["view"]))

    def test_single_saved_on_secondary_maps_to_primary(self):
        displays = [monitor(), monitor("b", 400, primary=False)]
        saved = make_layout(state(displays, [("one", "One", "b", 1, 1)]))
        current = state(displays, [("one", "One", "b", 0, 0)])
        self.assertEqual(plan_restore(saved, current)["positions"]["one"], [100, 100])

    def test_one_screen_save_two_screen_restore(self):
        current = deepcopy(self.base)
        current["monitors"].append(monitor("b", 400, primary=False))
        self.assertEqual(plan_restore(self.saved, current)["positions"], positions(self.base))

    def test_single_screen_missing_metadata_allowed(self):
        for m in self.saved["monitors"] + self.base["monitors"]:
            m["device_id"], m["scale"] = None, None
        self.assertEqual(plan_restore(self.saved, self.base)["positions"], positions(self.base))

    def multi_base(self):
        return state([monitor(), monitor("b", 400, primary=False)], [("one", "One", "a", 1, 1), ("two", "Two", "b", 2, 2)])

    def test_multi_screen_rearrangement_primary_change_extra_display(self):
        saved = make_layout(self.multi_base())
        displays = [
            monitor("renamed-a", -400, primary=False, device="physical-a"),
            monitor("renamed-b", 0, device="physical-b"),
            monitor("c", 400, primary=False),
        ]
        current = state(displays, [("one", "One", "renamed-b", 0, 0), ("two", "Two", "renamed-a", 0, 0), ("new", "New", "c", 0, 0)])
        plan = plan_restore(saved, current)
        self.assertFalse(plan["single_screen"])
        self.assertEqual(plan["positions"], {"one": [-300, 100], "two": [200, 200], "new": [0, 0]})
        self.assert_valid(current, plan)

    def test_multi_missing_display_with_survivors_rejected(self):
        saved = make_layout(self.multi_base())
        current = state(specs=[("one", "One", "a", 0, 0), ("two", "Two", "a", 1, 0)])
        with self.assertRaisesRegex(LayoutError, "跨屏布局无法可靠匹配"):
            plan_restore(saved, current)

    def test_multi_missing_display_without_survivors_ignored(self):
        saved = make_layout(self.multi_base())
        current = state(specs=[("one", "One", "a", 0, 0), ("new", "New", "a", 1, 0)])
        plan = plan_restore(saved, current)
        self.assertEqual(plan["positions"], {"one": [100, 100], "new": [0, 0]})
        self.assertTrue(plan["notes"])

    def test_multi_ambiguous_device_identity_rejected(self):
        base = self.multi_base()
        saved = make_layout(base)
        base["monitors"].append(monitor("c", 800, primary=False, device="physical-b"))
        with self.assertRaisesRegex(LayoutError, "无法可靠匹配"):
            plan_restore(saved, base)

    def test_negative_coordinates_and_view_offset_round_trip(self):
        current = state([monitor(x=-400, y=-100)], [("one", "One", "a", 1, 1)], origin=(-450, -149))
        saved = make_layout(current)
        self.assertEqual(plan_restore(saved, current)["positions"], positions(current))
        self.assertEqual(saved["icons"][0]["local"], [150, 151])

    def test_auto_arrange_rejected(self):
        self.base["auto_arrange"] = True
        with self.assertRaisesRegex(LayoutError, "自动排列"):
            plan_restore(self.saved, self.base)

    def test_zero_icons_valid(self):
        current = state()
        plan = plan_restore(make_layout(current), current)
        self.assertEqual(plan["positions"], {})
        current["icons"].append({"id": "new", "name": "A", "position": [0, 0]})
        self.assertEqual(plan_restore(make_layout(state()), current)["positions"], {"new": [0, 0]})

    def test_invalid_schema_rejected(self):
        for mutate in (
            lambda d: d.update(version=2),
            lambda d: d.update(version=True),
            lambda d: d["view"].update(spacing=[0, 100]),
            lambda d: d["icons"][0].update(local=[123, 456]),
            lambda d: d["icons"][0].update(grid=[99, 99]),
            lambda d: d["icons"][0].update(position=[True, 0]),
            lambda d: d["monitors"][0].update(primary=False),
            lambda d: d.update(monitor_count=2),
            lambda d: d.update(saved_at="bad"),
        ):
            corrupted = deepcopy(self.saved)
            mutate(corrupted)
            with self.assertRaises(LayoutError):
                validate_layout(corrupted)

    def test_verification_detects_mismatch_overlap_and_outside(self):
        current = deepcopy(self.base)
        current["icons"][1]["position"] = list(current["icons"][0]["position"])
        self.assertTrue(any("重叠" in e for e in verify_positions(current, positions(self.base))))
        current["icons"][1]["position"] = [390, 390]
        self.assertTrue(any("越界" in e for e in verify_positions(current, positions(current))))
        current["icons"][1]["position"] = [200, 203]
        self.assertEqual(verify_positions(current, positions(self.base), tolerance=4), [])

    def test_deterministic_randomized_layouts(self):
        rng = random.Random(1234)
        for _ in range(80):
            positions_old = rng.sample([(x, y) for x in range(6) for y in range(6)], 14)
            base = state([monitor(width=600, height=600)], [(str(i), f"Icon{i}", "a", x, y) for i, (x, y) in enumerate(positions_old)])
            saved = make_layout(base)
            current = deepcopy(base)
            current["icons"] = [icon for icon in current["icons"] if rng.random() > 0.3]
            current["icons"] += [{"id": f"new{i}", "name": f"New{i}", "position": [0, 0]} for i in range(5)]
            current["monitors"][0] = monitor(width=400, height=600)
            rng.shuffle(current["icons"])
            plan = plan_restore(saved, current)
            self.assert_valid(current, plan)
            self.assertEqual(plan_restore(saved, apply_plan(current, plan)), plan)


class StorageTests(unittest.TestCase):
    def test_utf8_atomic_round_trip(self):
        data = make_layout(state(specs=[("文件.lnk", "快捷方式", "a", 0, 0)]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "layout.json"
            atomic_save(path, data)
            self.assertEqual(load_layout(path), data)
            self.assertIn("快捷方式", path.read_text(encoding="utf-8"))

    def test_failed_replace_preserves_old_file_and_removes_temporary(self):
        data = make_layout(state())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "layout.json"
            path.write_bytes(b"original")
            with patch("layout.os.replace", side_effect=PermissionError("locked")), self.assertRaises(PermissionError):
                atomic_save(path, data)
            self.assertEqual(path.read_bytes(), b"original")
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_corrupt_duplicate_and_invalid_encoding_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "layout.json"
            for content in (b"{", b'{"version":1,"version":2}', b"\xff\xfe", b"null", b"[]"):
                path.write_bytes(content)
                with self.assertRaises(LayoutError):
                    load_layout(path)


class FakeShell:
    def __init__(self, data, fail=False, sabotage=False):
        self.data, self.moves = deepcopy(data), []
        self.fail, self.sabotage, self.closed = fail, sabotage, False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def snapshot(self):
        return deepcopy(self.data)

    def move(self, targets):
        self.moves.append(deepcopy(targets))
        first = len(self.moves) == 1
        for icon in self.data["icons"]:
            if icon["id"] in targets:
                icon["position"] = list(targets[icon["id"]])
                if first and self.sabotage:
                    icon["position"][0] += 30
                if first and self.fail:
                    raise ShellError("模拟部分移动后的 COM 失败")


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "layout.json"
        self.baseline = state(specs=[("one", "A", "a", 1, 1), ("two", "B", "a", 2, 2)])
        atomic_save(self.path, make_layout(self.baseline))
        self.before = state(specs=[("one", "A", "a", 0, 0), ("two", "B", "a", 0, 1)])

    def test_success_and_repeat_does_not_write_json_or_move_again(self):
        shell = FakeShell(self.before)
        original = self.path.read_bytes()
        restore_layout(self.path, lambda: shell, lambda _: None)
        self.assertEqual(positions(shell.data), positions(self.baseline))
        restore_layout(self.path, lambda: shell, lambda _: None)
        self.assertEqual(len(shell.moves), 1)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertTrue(shell.closed)

    def test_partial_com_failure_rolls_back(self):
        shell = FakeShell(self.before, fail=True)
        original = self.path.read_bytes()
        with self.assertRaisesRegex(LayoutError, "已回退并核对"):
            restore_layout(self.path, lambda: shell, lambda _: None)
        self.assertEqual(positions(shell.data), positions(self.before))
        self.assertEqual(self.path.read_bytes(), original)

    def test_verification_failure_rolls_back(self):
        shell = FakeShell(self.before, sabotage=True)
        with self.assertRaisesRegex(LayoutError, "已回退并核对"):
            restore_layout(self.path, lambda: shell, lambda _: None)
        self.assertEqual(positions(shell.data), positions(self.before))

    def test_bad_json_never_opens_shell(self):
        self.path.write_text("{", encoding="utf-8")
        with self.assertRaises(LayoutError):
            restore_layout(self.path, lambda: self.fail("不能调用 Shell"))

    def test_desk_changes_before_move_rejected(self):
        shell = FakeShell(self.before)
        read = shell.snapshot
        count = 0

        def snapshot():
            nonlocal count
            result = read()
            count += 1
            if count > 1:
                result["icons"][0]["position"][0] += 10
            return result

        shell.snapshot = snapshot
        with self.assertRaisesRegex(LayoutError, "计算期间"):
            restore_layout(self.path, lambda: shell, lambda _: None)
        self.assertEqual(shell.moves, [])

    def test_save_resets_baseline(self):
        shell = FakeShell(self.before)
        save_layout(self.path, lambda: shell)
        self.assertEqual(positions(load_layout(self.path)), positions(self.before))
        self.assertEqual(shell.moves, [])


class AbiTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32" and ctypes.sizeof(ctypes.c_void_p) == 8, "Windows x64 ABI")
    def test_native_struct_sizes(self):
        self.assertEqual(ctypes.sizeof(VARIANT), 24)
        self.assertEqual(ctypes.sizeof(STRRET), 272)
        self.assertEqual(ctypes.sizeof(GUID), 16)

    def test_hresult_s_false_is_not_failure(self):
        self.assertEqual(check(1, "GetAutoArrange"), 1)
        with self.assertRaises(ShellError):
            check(-2147467259, "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import layout
import library

TEMPLATE = Path(__file__).resolve().parents[1] / "template" / "desktop_neptune.vdf"


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.dest = self.tmp / "controller_neptune.vdf"
        shutil.copy(TEMPLATE, self.dest)
        self.original = self.dest.read_bytes()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_hold_b_library_writes_nothing(self):
        status, wrote = layout.apply_folder(self.tmp, library.defaults())
        self.assertFalse(wrote)
        self.assertEqual(status, "This file has no mode shift to edit.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_plain_key_change_backs_up_and_touches_one_binding(self):
        row = library.blank()
        row.update(name="Down on up", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertTrue(wrote)
        self.assertTrue(status.startswith("Backed up to backup-"))
        updated = self.dest.read_text(encoding="utf-8")
        original = self.original.decode("utf-8")
        self.assertEqual(original.count("key_press UP_ARROW"), 2)
        self.assertEqual(updated.count("key_press UP_ARROW"), 1)
        self.assertEqual(updated.count("key_press DOWN_ARROW"), original.count("key_press DOWN_ARROW") + 1)
        backup = next(self.tmp.glob("backup-*")) / "controller_neptune.vdf"
        self.assertEqual(hashlib.sha256(backup.read_bytes()).digest(), hashlib.sha256(self.original).digest())
        self.assertTrue((self.tmp / "where-to-put-this.txt").is_file())

    def test_second_write_does_not_backup_again(self):
        row = library.blank()
        row.update(control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        layout.apply_folder(self.tmp, [row])
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertFalse(wrote)
        self.assertIn("Already this change", status)
        self.assertEqual(len(list(self.tmp.glob("backup-*"))), 1)

    def test_start_press_keeps_the_long_press(self):
        row = library.blank()
        row.update(control="Start", action="Keyboard", key="Tab", **{"and": "none"})
        layout.apply_folder(self.tmp, [row])
        text = self.dest.read_text(encoding="utf-8")
        self.assertIn("controller_action CHANGE_PRESET 2 1 1", text)

    def test_missing_file(self):
        self.dest.unlink()
        status, wrote = layout.apply_folder(self.tmp, [library.blank()])
        self.assertFalse(wrote)
        self.assertEqual(status, "Copy the Deck's current file into the folder first.")

    def _directions(self, up="Up Arrow", down="Down Arrow", left="Left Arrow", right="Right Arrow"):
        specs = (
            ("Up", "D-pad up", up),
            ("Down", "D-pad down", down),
            ("Left", "D-pad left", left),
            ("Right", "D-pad right", right),
        )
        rows = []
        for name, control, key in specs:
            row = library.blank()
            row.update(name=name, control=control, action="Keyboard", key=key, **{"and": "none"})
            rows.append(row)
        return rows

    def test_no_folder(self):
        status, can_write = layout.assess("", [library.blank()])
        self.assertFalse(can_write)
        self.assertEqual(status, "pick a folder.")

    def test_empty_file_says_seed_is_missing(self):
        self.dest.write_bytes(b"")
        status, wrote = layout.apply_folder(self.tmp, self._directions())
        self.assertFalse(wrote)
        self.assertEqual(status, "Seed is missing.")

    def test_other_file_says_seed_is_missing(self):
        self.dest.write_text("not a desktop layout\n", encoding="utf-8")
        status, wrote = layout.apply_folder(self.tmp, self._directions())
        self.assertFalse(wrote)
        self.assertEqual(status, "Seed is missing.")
        self.assertEqual(self.dest.read_text(encoding="utf-8"), "not a desktop layout\n")

    def test_unknown_key_is_named(self):
        row = library.blank()
        row.update(control="D-pad up", action="Keyboard", key="Not A Key", **{"and": "none"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertFalse(wrote)
        self.assertEqual(status, "No binding text for Not A Key.")
        self.assertEqual(self.dest.read_bytes(), self.original)

    def test_second_key_is_refused(self):
        row = library.blank()
        row.update(control="D-pad up", action="Keyboard", key="Up Arrow", **{"and": "Left Alt"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertFalse(wrote)
        self.assertEqual(status, "No binding text for Left Alt.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_four_matching_directions_do_not_backup(self):
        status, wrote = layout.apply_folder(self.tmp, self._directions())
        self.assertFalse(wrote)
        self.assertEqual(status, "Already this change. Nothing to write.")
        self.assertEqual(list(self.tmp.glob("backup-*")), [])
        self.assertEqual(self.dest.read_bytes(), self.original)

    def test_one_direction_changes_and_the_other_three_stay(self):
        parent = set(self.tmp.parent.iterdir())
        status, wrote = layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        self.assertTrue(wrote)
        self.assertTrue(status.startswith("Backed up to backup-"))
        updated = self.dest.read_text(encoding="utf-8")
        original = self.original.decode("utf-8")
        diffs = [i for i, (old, new) in enumerate(zip(original.splitlines(), updated.splitlines())) if old != new]
        self.assertEqual(len(diffs), 1)
        self.assertIn("key_press DOWN_ARROW", updated.splitlines()[diffs[0]])
        self.assertIn("key_press LEFT_ARROW", updated)
        self.assertIn("key_press RIGHT_ARROW", updated)
        backup = next(self.tmp.glob("backup-*")) / "controller_neptune.vdf"
        self.assertEqual(hashlib.sha256(backup.read_bytes()).digest(), hashlib.sha256(self.original).digest())
        names = sorted(path.name for path in self.tmp.iterdir() if not path.name.startswith("backup-"))
        self.assertEqual(names, ["controller_neptune.vdf", "where-to-put-this.txt"])
        self.assertEqual(set(self.tmp.parent.iterdir()), parent)

    def test_older_backup_is_left_in_place(self):
        layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        first = next(self.tmp.glob("backup-*"))
        first_bytes = (first / "controller_neptune.vdf").read_bytes()
        status, wrote = layout.apply_folder(self.tmp, self._directions(up="Left Arrow"))
        self.assertTrue(wrote)
        self.assertEqual((first / "controller_neptune.vdf").read_bytes(), first_bytes)
        self.assertEqual(len(list(self.tmp.glob("backup-*"))), 2)
        self.assertTrue(status.startswith("Backed up to backup-"))

    def test_bad_backup_removes_only_the_new_file(self):
        real_copy = layout.shutil.copy2

        def bad_copy(src, dst, *args, **kwargs):
            real_copy(src, dst, *args, **kwargs)
            Path(dst).write_bytes(b"not the file")

        layout.shutil.copy2 = bad_copy
        try:
            status, wrote = layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        finally:
            layout.shutil.copy2 = real_copy
        self.assertFalse(wrote)
        self.assertEqual(status, "Backup failed. The current file was left as it was.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_unwritable_folder_leaves_the_earlier_backup(self):
        layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        kept = self.dest.read_bytes()
        earlier = (next(self.tmp.glob("backup-*")) / "controller_neptune.vdf").read_bytes()
        os.chmod(self.tmp, 0o500)
        try:
            status, wrote = layout.apply_folder(self.tmp, self._directions(up="Left Arrow"))
        finally:
            os.chmod(self.tmp, 0o700)
        self.assertFalse(wrote)
        self.assertEqual(status, "Could not write. The current file was left as it was.")
        self.assertEqual(self.dest.read_bytes(), kept)
        self.assertEqual((next(self.tmp.glob("backup-*")) / "controller_neptune.vdf").read_bytes(), earlier)
        self.assertEqual(len(list(self.tmp.glob("backup-*"))), 1)

    def test_interrupted_replace_restores_the_file(self):
        real_replace = layout.os.replace

        def fail_replace(*args, **kwargs):
            raise OSError("pulled")

        layout.os.replace = fail_replace
        try:
            status, wrote = layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        finally:
            layout.os.replace = real_replace
        self.assertFalse(wrote)
        self.assertTrue(status.startswith("Could not write the layout. The previous file is in backup-"))
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("*.writing")), [])
        backup = next(self.tmp.glob("backup-*")) / "controller_neptune.vdf"
        self.assertEqual(backup.read_bytes(), self.original)

    def test_failed_replace_does_not_empty_the_file(self):
        real_replace = layout.os.replace
        real_copy = layout.shutil.copy2
        copies = {"n": 0}

        def fail_replace(*args, **kwargs):
            raise OSError("pulled")

        def truncate_then_fail(src, dst, *args, **kwargs):
            copies["n"] += 1
            if copies["n"] == 1:
                return real_copy(src, dst, *args, **kwargs)
            Path(dst).write_bytes(b"")
            raise OSError("short restore")

        layout.os.replace = fail_replace
        layout.shutil.copy2 = truncate_then_fail
        try:
            status, wrote = layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        finally:
            layout.os.replace = real_replace
            layout.shutil.copy2 = real_copy
        self.assertFalse(wrote)
        self.assertTrue(status.startswith("Could not write the layout. The previous file is in backup-"))
        self.assertEqual(self.dest.read_bytes(), self.original)

    def test_screenshot_is_not_invented(self):
        row = library.blank()
        row.update(control="D-pad up", action="Screenshot", **{"and": "none"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertFalse(wrote)
        self.assertEqual(status, "No binding text for Screenshot.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertNotIn(b"SCREENSHOT", self.dest.read_bytes())

    def test_same_control_twice_is_refused(self):
        first = library.blank()
        first.update(name="One", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        second = library.blank()
        second.update(name="Two", control="D-pad up", action="Keyboard", key="Up Arrow", **{"and": "none"})
        status, wrote = layout.apply_folder(self.tmp, [first, second])
        self.assertFalse(wrote)
        self.assertEqual(status, "D-pad up is set more than once.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_note_uses_the_plan_text(self):
        layout.apply_folder(self.tmp, self._directions(up="Down Arrow"))
        note = (self.tmp / "where-to-put-this.txt").read_text(encoding="utf-8")
        self.assertIn("Do not copy the backup folder onto the Deck unless you are undoing this.", note)
        self.assertIn("2. Copy this stick's controller_neptune.vdf over that file.", note)

    def _outside(self):
        path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, path, True)
        return path

    def _down_row(self):
        row = library.blank()
        row.update(control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        return row

    def test_symlink_dest_is_refused(self):
        outside = self._outside()
        target = outside / "controller_neptune.vdf"
        target.write_bytes(self.original)
        self.dest.unlink()
        self.dest.symlink_to(target)
        status, wrote = layout.apply_folder(self.tmp, [self._down_row()])
        self.assertFalse(wrote)
        self.assertEqual(status, "That file points outside this folder.")
        self.assertEqual(target.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_symlink_note_is_refused(self):
        outside = self._outside()
        victim = outside / "where-to-put-this.txt"
        victim.write_text("keep", encoding="utf-8")
        (self.tmp / "where-to-put-this.txt").symlink_to(victim)
        status, wrote = layout.apply_folder(self.tmp, [self._down_row()])
        self.assertFalse(wrote)
        self.assertEqual(status, "That file points outside this folder.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(victim.read_text(encoding="utf-8"), "keep")
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_symlink_writing_file_is_refused(self):
        outside = self._outside()
        victim = outside / "victim.txt"
        victim.write_text("keep", encoding="utf-8")
        (self.tmp / "controller_neptune.vdf.writing").symlink_to(victim)
        status, wrote = layout.apply_folder(self.tmp, [self._down_row()])
        self.assertFalse(wrote)
        self.assertEqual(status, "That file points outside this folder.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(victim.read_text(encoding="utf-8"), "keep")
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def _binding_line(self, value):
        return '\t\t\t\t\t\t\t"binding"\t\t"%s"' % value

    def _hold_rows(self, up="Up Arrow"):
        specs = (
            ("Parent folder", "Up, hold B", up, "Left Alt"),
            ("Open", "Down, hold B", "Enter", "none"),
            ("Back", "Left, hold B", "Left Arrow", "Left Alt"),
            ("Forward", "Right, hold B", "Right Arrow", "Left Alt"),
        )
        rows = []
        for name, control, key, second in specs:
            row = library.blank()
            row.update(name=name, control=control, action="Keyboard", key=key, **{"and": second})
            rows.append(row)
        return rows

    def _install_hold_group(self, north_second="key_press UP_ARROW", drop_north=False):
        text = self.dest.read_bytes().decode("utf-8")
        newline = "\r\n" if "\r\n" in text else "\n"
        escape = self._binding_line("key_press ESCAPE")
        self.assertEqual(text.count(escape), 2)
        text = text.replace(escape, self._binding_line("mode_shift dpad 90"), 1)
        start, end = layout._group_slice(text, "9")
        shifted = text[start:end].replace('\t\t"id"\t\t"9"', '\t\t"id"\t\t"90"', 1)
        self.assertNotEqual(shifted, text[start:end])
        replacements = (
            ("key_press UP_ARROW", ["key_press LEFT_ALT", north_second]),
            ("key_press DOWN_ARROW", ["key_press RETURN"]),
            ("key_press RIGHT_ARROW", ["key_press LEFT_ALT", "key_press RIGHT_ARROW"]),
            ("key_press LEFT_ARROW", ["key_press LEFT_ALT", "key_press LEFT_ARROW"]),
        )
        for old, lines in replacements:
            old_line = self._binding_line(old)
            self.assertEqual(shifted.count(old_line), 1, old)
            new = newline.join(self._binding_line(line) for line in lines)
            shifted = shifted.replace(old_line, new, 1)
        if drop_north:
            at = shifted.find('"dpad_north"')
            self.assertGreaterEqual(at, 0)
            shifted = shifted[:at] + '"dpad_gone"' + shifted[at + len('"dpad_north"'):]
        text = text[:end] + shifted + text[end:]
        self.dest.write_bytes(text.encode("utf-8"))
        return text

    def test_hold_b_changes_one_direction_when_the_file_has_the_slots(self):
        before = self._install_hold_group()
        status, wrote = layout.apply_folder(self.tmp, self._hold_rows(up="Down Arrow"))
        self.assertTrue(wrote, status)
        self.assertTrue(status.startswith("Backed up to backup-"))
        after = self.dest.read_bytes().decode("utf-8")
        before_lines = before.splitlines()
        after_lines = after.splitlines()
        self.assertEqual(len(before_lines), len(after_lines))
        diffs = [i for i, (old, new) in enumerate(zip(before_lines, after_lines)) if old != new]
        self.assertEqual(len(diffs), 1)
        self.assertIn("key_press DOWN_ARROW", after_lines[diffs[0]])
        self.assertIn("key_press LEFT_ALT", after_lines[diffs[0] - 1])
        bstart, bend = layout._group_slice(before, "9")
        astart, aend = layout._group_slice(after, "9")
        self.assertEqual(after[astart:aend], before[bstart:bend])
        self.assertEqual(before.count("mode_shift dpad 90"), 1)
        self.assertEqual(after.count("mode_shift dpad 90"), 1)
        backup = next(self.tmp.glob("backup-*")) / "controller_neptune.vdf"
        self.assertEqual(backup.read_bytes(), before.encode("utf-8"))
        self.assertTrue((self.tmp / "where-to-put-this.txt").is_file())

    def test_hold_b_wrong_mode_writes_nothing(self):
        text = self.dest.read_bytes().decode("utf-8")
        escape = self._binding_line("key_press ESCAPE")
        text = text.replace(escape, self._binding_line("mode_shift joystick_mouse 9"), 1)
        self.dest.write_bytes(text.encode("utf-8"))
        row = library.blank()
        row.update(control="Up, hold B", action="Keyboard", key="Down Arrow", **{"and": "Left Alt"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertFalse(wrote)
        self.assertEqual(status, "This file has no mode shift to edit.")
        self.assertEqual(self.dest.read_bytes(), text.encode("utf-8"))
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_hold_b_missing_input_is_named(self):
        before = self._install_hold_group(drop_north=True)
        row = library.blank()
        row.update(control="Up, hold B", action="Keyboard", key="Up Arrow", **{"and": "Left Alt"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertFalse(wrote)
        self.assertEqual(status, "This file has no slot for that control.")
        self.assertEqual(self.dest.read_bytes(), before.encode("utf-8"))
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_second_key_writes_when_the_line_is_there(self):
        text = self.dest.read_bytes().decode("utf-8")
        newline = "\r\n" if "\r\n" in text else "\n"
        line = self._binding_line("key_press UP_ARROW")
        extra = self._binding_line("key_press LEFT_ALT") + newline + line
        text = text.replace(line, extra, 1)
        self.dest.write_bytes(text.encode("utf-8"))
        row = library.blank()
        row.update(name="Parent", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "Left Alt"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertTrue(wrote, status)
        after = self.dest.read_bytes().decode("utf-8")
        diffs = [i for i, (old, new) in enumerate(zip(text.splitlines(), after.splitlines())) if old != new]
        self.assertEqual(len(diffs), 1)
        self.assertIn("key_press DOWN_ARROW", after.splitlines()[diffs[0]])
        self.assertEqual(after.count("key_press UP_ARROW"), text.count("key_press UP_ARROW") - 1)
        self.assertEqual(after.count("key_press LEFT_ALT"), text.count("key_press LEFT_ALT"))

    def test_script_row_blocks_the_whole_list(self):
        plain = library.blank()
        plain.update(name="Down on up", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        script = library.blank()
        script.update(name="Files", control="A", action="Run script", command="dolphin")
        status, wrote = layout.apply_folder(self.tmp, [plain, script])
        self.assertFalse(wrote)
        self.assertEqual(status, "Files is a script. A script is not written into this file.")
        self.assertEqual(self.dest.read_bytes(), self.original)
        self.assertEqual(list(self.tmp.glob("backup-*")), [])

    def test_kind_names(self):
        self.assertEqual(library.kind_of("Keyboard"), "Shortcut")
        self.assertEqual(library.kind_of("Run script"), "Script")
        self.assertEqual(library.kind_of("Screenshot"), "System command")

    def test_disabled_script_row_does_not_block_write(self):
        plain = library.blank()
        plain.update(name="Down on up", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        script = library.blank()
        script.update(name="Files", enabled=False, control="A", action="Run script", command="dolphin")
        status, wrote = layout.apply_folder(self.tmp, [plain, script])
        self.assertTrue(wrote, status)

    def test_restore_backup_restores_newest_backup(self):
        row = library.blank()
        row.update(name="Down on up", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertTrue(wrote, status)
        self.assertNotEqual(self.dest.read_bytes(), self.original)
        status, restored = layout.restore_backup(self.tmp)
        self.assertTrue(restored, status)
        self.assertEqual(self.dest.read_bytes(), self.original)

    def test_restore_stock_backs_up_and_restores_default(self):
        row = library.blank()
        row.update(name="Down on up", control="D-pad up", action="Keyboard", key="Down Arrow", **{"and": "none"})
        status, wrote = layout.apply_folder(self.tmp, [row])
        self.assertTrue(wrote, status)
        status, restored = layout.restore_stock(self.tmp)
        self.assertTrue(restored, status)
        self.assertEqual(self.dest.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()

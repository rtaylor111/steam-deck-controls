"""Backup a desktop layout file and replace bindings that already have a slot.

A hold-B control is written only when button B already has a mode_shift
binding and the group it names has the same mode and the input. The stock
desktop file has no such binding, so that library is refused. A second key
is written only when that press already has a second binding line.
"""

import hashlib
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

TARGET_NAME = "controller_neptune.vdf"

# group id, input name, activator that holds the binding we may replace
SLOTS = {
    "D-pad up": ("9", "dpad_north", "Full_Press"),
    "D-pad down": ("9", "dpad_south", "Full_Press"),
    "D-pad left": ("9", "dpad_west", "Full_Press"),
    "D-pad right": ("9", "dpad_east", "Full_Press"),
    "A": ("0", "button_a", "Full_Press"),
    "B": ("0", "button_b", "Full_Press"),
    "X": ("0", "button_x", "Full_Press"),
    "Y": ("0", "button_y", "Full_Press"),
    "Left bumper": ("7", "left_bumper", "Full_Press"),
    "Right bumper": ("7", "right_bumper", "Full_Press"),
    "Left grip": ("7", "button_back_left", "Full_Press"),
    "Right grip": ("7", "button_back_right", "Full_Press"),
    "Left grip upper": ("7", "button_back_left_upper", "Full_Press"),
    "Right grip upper": ("7", "button_back_right_upper", "Full_Press"),
    "Start": ("7", "button_escape", "Full_Press"),
    "Select": ("7", "button_menu", "Full_Press"),
}

# Hold-B edits the group named by button B's mode_shift binding.
# That binding's shape is the one in basicui: mode_shift right_joystick 59.
# The mode word and the group id are read from the file.
HOLD_INPUT = {
    "Up, hold B": "dpad_north",
    "Down, hold B": "dpad_south",
    "Left, hold B": "dpad_west",
    "Right, hold B": "dpad_east",
    "Left grip, hold B": "button_back_left",
    "Right grip, hold B": "button_back_right",
}

KEYS = {
    "Up Arrow": "UP_ARROW",
    "Down Arrow": "DOWN_ARROW",
    "Left Arrow": "LEFT_ARROW",
    "Right Arrow": "RIGHT_ARROW",
    "Enter": "RETURN",
    "Escape": "ESCAPE",
    "Space": "SPACE",
    "Tab": "TAB",
    "Page Up": "PAGE_UP",
    "Page Down": "PAGE_DOWN",
    "Left Alt": "LEFT_ALT",
    "Left Ctrl": "LEFT_CONTROL",
    "Left Shift": "LEFT_SHIFT",
    "Windows": "LEFT_WINDOWS",
}

SYSTEM = {
    "Show keyboard": "controller_action SHOW_KEYBOARD",
    "Screenshot": "controller_action SCREENSHOT",
    "Magnifier": "controller_action toggle_magnifier",
    "Brighter": "controller_action brightness_up",
    "Dimmer": "controller_action brightness_down",
    "Quit": "controller_action quit_application",
    "Steam": "controller_action system_key_1",
    "Record": "controller_action gr_toggle",
    "Marker": "controller_action gr_marker",
    "Clip": "controller_action gr_clip",
    "Screen reader": "controller_action sr_enable",
}

PADS = {
    "A": "xinput_button A",
    "B": "xinput_button B",
    "X": "xinput_button X",
    "Y": "xinput_button Y",
    "D-pad up": "xinput_button DPAD_UP",
    "D-pad down": "xinput_button DPAD_DOWN",
    "D-pad left": "xinput_button DPAD_LEFT",
    "D-pad right": "xinput_button DPAD_RIGHT",
    "Start": "xinput_button START",
    "Select": "xinput_button SELECT",
    "Left bumper": "xinput_button shoulder_left",
    "Right bumper": "xinput_button shoulder_right",
}


def binding_for(row):
    """Return the binding texts for a row, or a reason it cannot be written.

    Two keys use the chord.vdf order: the modifier, then the key.
    """
    control = row.get("control", "")
    if control not in SLOTS and control not in HOLD_INPUT:
        return None, "This file has no mode shift to edit."
    action = row.get("action", "")
    if action == "Keyboard":
        token = KEYS.get(row.get("key", ""))
        if not token:
            return None, "No binding text for %s." % row.get("key", "that key")
        second = row.get("and", "none")
        if second in ("", "none"):
            return ["key_press %s" % token], ""
        sub = KEYS.get(second)
        if not sub:
            return None, "No binding text for %s." % second
        return ["key_press %s" % sub, "key_press %s" % token], ""
    if action == "Run script":
        name = row.get("name") or "That shortcut"
        return None, "%s is a script. A script is not written into this file." % name
    if action == "Mouse button":
        side = {"Left": "LEFT", "Right": "RIGHT", "Middle": "MIDDLE"}.get(row.get("mouse", ""))
        if not side:
            return None, "No binding text for that mouse button."
        return ["mouse_button %s" % side], ""
    if action == "Mouse wheel":
        way = {"Up": "SCROLL_UP", "Down": "SCROLL_DOWN"}.get(row.get("wheel", ""))
        if not way:
            return None, "No binding text for that wheel."
        return ["mouse_wheel %s" % way], ""
    if action == "Gamepad button":
        text = PADS.get(row.get("pad", ""))
        if not text:
            return None, "No binding text for that gamepad button."
        return [text], ""
    if action == "Change preset":
        return None, "No binding text for Change preset."
    if action in SYSTEM:
        return [SYSTEM[action]], ""
    return None, "No binding text for %s." % (action or "that action")


def _group_slice(text, group_id):
    starts = [match.start() for match in re.finditer(r'"group"', text)]
    id_pattern = re.compile(r'"id"\s+"%s"' % re.escape(group_id))
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        chunk = text[start:end]
        if id_pattern.search(chunk[:300]):
            return start, end
    return None


# basicui writes this as one binding: mode_shift right_joystick 59.
# The mode word and the group id are read from the file. Nothing here adds one.
_MODE_SHIFT = re.compile(r"^mode_shift\s+(\w+)\s+(\d+)$")


def _binding_spans(chunk, activator_at):
    """Quoted binding values inside the bindings block after this activator.

    The first closing brace ends the block. Offsets are into chunk.
    None means the block is not there.
    """
    bindings_at = chunk.find('"bindings"', activator_at)
    if bindings_at < 0:
        return None
    brace = chunk.find("{", bindings_at)
    if brace < 0:
        return None
    close = chunk.find("}", brace)
    if close < 0:
        return None
    block = chunk[brace + 1:close]
    spans = []
    pos = 0
    while True:
        key_at = block.find('"binding"', pos)
        if key_at < 0:
            break
        quote = block.find('"', key_at + len('"binding"'))
        if quote < 0:
            break
        quote2 = block.find('"', quote + 1)
        if quote2 < 0:
            break
        spans.append((brace + 1 + quote + 1, brace + 1 + quote2))
        pos = quote2 + 1
    return spans


def _first_binding(chunk, input_name, activator):
    input_at = chunk.find('"%s"' % input_name)
    if input_at < 0:
        return None
    activator_at = chunk.find('"%s"' % activator, input_at)
    if activator_at < 0:
        return None
    spans = _binding_spans(chunk, activator_at)
    if not spans:
        return None
    start, end = spans[0]
    return chunk[start:end].strip()


def _hold_slot(text, control):
    found = None
    starts = [match.start() for match in re.finditer(r'"group"', text)]
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        value = _first_binding(text[start:end], "button_b", "Full_Press")
        if not value:
            continue
        match = _MODE_SHIFT.match(value)
        if match:
            found = match
            break
    if not found:
        return None, "This file has no mode shift to edit."
    mode_word, group_id = found.group(1), found.group(2)
    target = _group_slice(text, group_id)
    if not target:
        return None, "This file has no mode shift to edit."
    chunk = text[target[0]:target[1]]
    mode = re.search(r'"mode"\s+"([^"]+)"', chunk[:400])
    if not mode or mode.group(1) != mode_word:
        return None, "This file has no mode shift to edit."
    input_name = HOLD_INPUT[control]
    if chunk.find('"%s"' % input_name) < 0:
        return None, "This file has no slot for that control."
    return (group_id, input_name, "Full_Press"), ""


def slot_for(text, control):
    if control in SLOTS:
        return SLOTS[control], ""
    if control in HOLD_INPUT:
        return _hold_slot(text, control)
    return None, "This file has no mode shift to edit."


def replace_bindings(text, group_id, input_name, activator, parts, row):
    found = _group_slice(text, group_id)
    if not found:
        return None, "This file has no slot for that control."
    start, end = found
    chunk = text[start:end]
    input_at = chunk.find('"%s"' % input_name)
    if input_at < 0:
        return None, "This file has no slot for that control."
    activator_at = chunk.find('"%s"' % activator, input_at)
    if activator_at < 0:
        return None, "This file has no press to edit."
    spans = _binding_spans(chunk, activator_at)
    if spans is None:
        return None, "This file has no press to edit."
    if len(spans) < len(parts):
        if len(parts) >= 2:
            return None, "No binding text for %s." % (row.get("and") or "that key")
        return None, "No binding text for %s." % _missing_label(row)
    updated = text
    # Later spans first, so an earlier span keeps its offset.
    for index in range(len(parts) - 1, -1, -1):
        span_start, span_end = spans[index]
        absolute = start + span_start
        absolute_end = start + span_end
        updated = updated[:absolute] + parts[index] + updated[absolute_end:]
    return updated, ""


def _missing_label(row):
    action = row.get("action", "")
    if action == "Keyboard":
        return row.get("key") or "that key"
    if action == "Gamepad button":
        return row.get("pad") or "that gamepad button"
    if action == "Mouse button":
        return row.get("mouse") or "that mouse button"
    if action == "Mouse wheel":
        return row.get("wheel") or "that wheel"
    return action or "that action"


def _part_label(row, index, count):
    if row.get("action") == "Keyboard" and count == 2 and index == 0:
        return row.get("and") or "that key"
    return _missing_label(row)


def plan_text(text, rows):
    active = [row for row in rows if row.get("enabled", True)]
    if not active:
        return None, "Turn on at least one shortcut."
    seen = {}
    for row in active:
        wanted, reason = binding_for(row)
        if reason:
            return None, reason
        for index, part in enumerate(wanted):
            if part not in text:
                return None, "No binding text for %s." % _part_label(row, index, len(wanted))
        control = row["control"]
        slot, reason = slot_for(text, control)
        if reason:
            return None, reason
        wanted_key = tuple(wanted)
        if control in seen and seen[control][0] != wanted_key:
            return None, "%s is set more than once." % control
        seen[control] = (wanted_key, row, slot)
    updated = text
    notes = []
    for control, (wanted, row, slot) in seen.items():
        group_id, input_name, activator = slot
        updated, reason = replace_bindings(updated, group_id, input_name, activator, list(wanted), row)
        if reason:
            return None, reason
        notes.append("%s: %s" % (row.get("name") or control, ", ".join(wanted)))
    return updated, notes


def _is_desktop(text):
    return (
        '"Desktop Configuration"' in text
        and '"controller_type"' in text
        and '"controller_neptune"' in text
    )


def _points_outside(folder):
    """True when the layout, the temp file, or the note resolves outside folder."""
    root = Path(folder).resolve()
    for name in (TARGET_NAME, TARGET_NAME + ".writing", "where-to-put-this.txt"):
        path = Path(folder) / name
        try:
            resolved = path.resolve()
        except OSError:
            return True
        try:
            resolved.relative_to(root)
        except ValueError:
            return True
    return False


def assess(folder, rows):
    """Return (status, can_write). Reads the folder. Writes nothing."""
    if not folder:
        return "pick a folder.", False
    if _points_outside(folder):
        return "That file points outside this folder.", False
    dest = Path(folder) / TARGET_NAME
    if not dest.is_file():
        return "Copy the Deck's current file into the folder first.", False
    try:
        text = dest.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return "Seed is missing.", False
    if not text.strip() or not _is_desktop(text):
        return "Seed is missing.", False
    updated, notes = plan_text(text, rows)
    if updated is None:
        return notes, False
    if updated == text:
        return "Already this change. Nothing to write.", False
    return "Current file found. Write will back it up first.", True


def _drop_new_backup(backup_dir, backup_file):
    """Remove the incomplete new backup file. Leave any older backup folder."""
    backup_file.unlink(missing_ok=True)
    try:
        backup_dir.rmdir()
    except OSError:
        pass


def apply_folder(folder, rows):
    """Write controller_neptune.vdf in folder. Returns (status, wrote)."""
    folder = Path(folder)
    status, can_write = assess(folder, rows)
    if not can_write:
        return status, False
    if _points_outside(folder):
        return "That file points outside this folder.", False
    dest = folder / TARGET_NAME
    original = dest.read_bytes().decode("utf-8")
    updated, notes = plan_text(original, rows)
    if updated is None or updated == original:
        return status, False
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = folder / ("backup-%s" % stamp)
    extra = 2
    while backup_dir.exists():
        backup_dir = folder / ("backup-%s-%s" % (stamp, extra))
        extra += 1
    backup_file = backup_dir / TARGET_NAME
    try:
        backup_dir.mkdir()
        shutil.copy2(dest, backup_file)
    except OSError:
        _drop_new_backup(backup_dir, backup_file)
        return "Could not write. The current file was left as it was.", False
    if hashlib.sha256(backup_file.read_bytes()).digest() != hashlib.sha256(dest.read_bytes()).digest():
        _drop_new_backup(backup_dir, backup_file)
        return "Backup failed. The current file was left as it was.", False
    temporary = folder / (TARGET_NAME + ".writing")
    try:
        temporary.write_bytes(updated.encode("utf-8"))
        if temporary.read_bytes().decode("utf-8") != updated:
            raise OSError("short write")
        os.replace(temporary, dest)
    except OSError:
        temporary.unlink(missing_ok=True)
        try:
            backup_bytes = backup_file.read_bytes()
        except OSError:
            return "Could not write the layout. The previous file is in %s." % backup_dir.name, False
        try:
            current = dest.read_bytes()
        except OSError:
            current = None
        if current != backup_bytes:
            restore = folder / (TARGET_NAME + ".restore")
            try:
                restore.write_bytes(backup_bytes)
                os.replace(restore, dest)
            except OSError:
                restore.unlink(missing_ok=True)
        return "Could not write the layout. The previous file is in %s." % backup_dir.name, False
    note = folder / "where-to-put-this.txt"
    try:
        note.write_text(_note(backup_dir.name, notes), encoding="utf-8")
    except OSError:
        return "Backed up to %s, then wrote this change. The placement note could not be written." % backup_dir.name, True
    return "Backed up to %s, then wrote this change." % backup_dir.name, True


def latest_backup(folder):
    """Return the newest backup directory in folder that holds TARGET_NAME, or None."""
    if not folder:
        return None
    root = Path(folder)
    if not root.is_dir():
        return None
    candidates = sorted(
        (p for p in root.iterdir() if p.is_dir() and not p.is_symlink() and p.name.startswith("backup-") and (p / TARGET_NAME).is_file() and not (p / TARGET_NAME).is_symlink()),
        key=lambda p: p.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def restore_backup(folder):
    """Restore TARGET_NAME from the newest backup-* folder. Returns (status, restored)."""
    if not folder:
        return "pick a folder.", False
    if _points_outside(folder):
        return "That file points outside this folder.", False
    backup_dir = latest_backup(folder)
    if backup_dir is None:
        return "No backup found in this folder.", False
    backup_file = backup_dir / TARGET_NAME
    try:
        backup_bytes = backup_file.read_bytes()
    except OSError:
        return "Could not read %s." % backup_dir.name, False
    dest = Path(folder) / TARGET_NAME
    temporary = Path(folder) / (TARGET_NAME + ".restoring")
    try:
        temporary.write_bytes(backup_bytes)
        if temporary.read_bytes() != backup_bytes:
            raise OSError("short write")
        os.replace(temporary, dest)
    except OSError:
        temporary.unlink(missing_ok=True)
        return "Could not restore from %s." % backup_dir.name, False
    return "Restored from %s." % backup_dir.name, True


def _note(backup_name, notes):
    lines = [
        "The previous file is in %s, next to this note." % backup_name,
        "To put it back: quit Steam, then copy that backup over controller_neptune.vdf",
        "in the Deck folder below. Do not copy the backup folder onto the Deck unless you are undoing this.",
        "",
        "Quit Steam completely before you copy the new file. If Steam is open it will overwrite the file.",
        "",
        "1. The file on the Deck is in the one numbered folder here:",
        "   /home/deck/.local/share/Steam/steamapps/common/Steam Controller Configs/<that folder>/config/413080/controller_neptune.vdf",
        "",
        "2. Copy this stick's controller_neptune.vdf over that file.",
        "",
        "3. Start Steam. Open Dolphin.",
        "   Hold B and press the D-pad. The four lines below are whatever the window wrote:",
    ]
    lines.extend("   " + line for line in notes)
    lines.extend([
        "   The D-pad alone still moves the highlight. A still opens. X is still the keyboard.",
        "",
        "The live path is also under Desktop Layout, the gear, Layout Details.",
        "",
        "If the old buttons come back, Steam's controller-config cloud put the old file back.",
        "The click path for turning that off has not been checked.",
        "",
    ])
    return "\n".join(lines)

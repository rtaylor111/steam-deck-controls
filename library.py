"""Named shortcuts saved on this PC."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIBRARY = HERE / "shortcuts.json"
SETTINGS = HERE / "settings.json"

SHORTCUT_ACTIONS = {"Keyboard", "Mouse button", "Mouse wheel", "Gamepad button"}
SYSTEM_ACTIONS = {
    "Show keyboard",
    "Screenshot",
    "Magnifier",
    "Brighter",
    "Dimmer",
    "Quit",
    "Change preset",
    "Steam",
    "Record",
    "Marker",
    "Clip",
    "Screen reader",
}

CONTROLS = [
    "Up, hold B",
    "Down, hold B",
    "Left, hold B",
    "Right, hold B",
    "Left grip, hold B",
    "Right grip, hold B",
    "D-pad up",
    "D-pad down",
    "D-pad left",
    "D-pad right",
    "A",
    "B",
    "X",
    "Y",
    "Left bumper",
    "Right bumper",
    "Left grip",
    "Right grip",
    "Left grip upper",
    "Right grip upper",
    "Start",
    "Select",
]

ACTIONS = ["Keyboard", "Run script", "Mouse button", "Mouse wheel", "Gamepad button", *sorted(SYSTEM_ACTIONS, key=str.lower)]

KEYS = [
    "Up Arrow",
    "Down Arrow",
    "Left Arrow",
    "Right Arrow",
    "Enter",
    "Escape",
    "Space",
    "Tab",
    "Page Up",
    "Page Down",
]
ANDS = ["none", "Left Alt", "Left Ctrl", "Left Shift", "Windows"]
MICE = ["Left", "Right", "Middle"]
WHEELS = ["Up", "Down"]
PADS = ["A", "B", "X", "Y", "D-pad up", "D-pad down", "D-pad left", "D-pad right", "Start", "Select", "Left bumper", "Right bumper"]
HOTKEYS = [
    "Left Ctrl + Page Up",
    "Left Ctrl + Page Down",
    "Left Shift + Page Up",
    "Left Alt + Page Up",
]


def kind_of(action):
    if action == "Run script":
        return "Script"
    if action in SYSTEM_ACTIONS:
        return "System command"
    return "Shortcut"


def blank():
    return {
        "name": "New shortcut",
        "enabled": True,
        "control": "D-pad up",
        "action": "Keyboard",
        "key": "Up Arrow",
        "and": "none",
        "command": "",
        "hotkey": HOTKEYS[0],
        "mouse": "Left",
        "wheel": "Up",
        "pad": "A",
    }


def defaults():
    rows = [
        ("Parent folder", "Up, hold B", "Up Arrow", "Left Alt"),
        ("Open", "Down, hold B", "Enter", "none"),
        ("Back", "Left, hold B", "Left Arrow", "Left Alt"),
        ("Forward", "Right, hold B", "Right Arrow", "Left Alt"),
    ]
    library = []
    for name, control, key, second in rows:
        row = blank()
        row.update(name=name, control=control, action="Keyboard", key=key, **{"and": second})
        library.append(row)
    files = blank()
    files.update(name="Files", enabled=False, control="Right grip, hold B", action="Run script", command="dolphin")
    library.append(files)
    return library


def load():
    if not LIBRARY.exists():
        rows = defaults()
        save(rows)
        return rows
    rows = json.loads(LIBRARY.read_text(encoding="utf-8"))
    cleaned = []
    for row in rows:
        item = blank()
        item.update(row)
        if "enabled" not in row and item.get("action") == "Run script":
            item["enabled"] = False
        cleaned.append(item)
    return cleaned


def save(rows):
    LIBRARY.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def load_folder():
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        folder = data.get("folder", "")
        return folder if isinstance(folder, str) and Path(folder).is_dir() else ""
    except (OSError, json.JSONDecodeError, AttributeError):
        return ""


def save_folder(folder):
    try:
        SETTINGS.write_text(json.dumps({"folder": folder}, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass

"""Deck screen. The saved list, then one shortcut. No keyboard is summoned."""

import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import library
import layout
import update

LIGHT = {
    "page": "#e6e6e6",
    "title": "#f7f7f7",
    "title_line": "#d6d6d6",
    "text": "#1c1c1c",
    "muted": "#5e5e5e",
    "body": "#ffffff",
    "box": "#d8d8d8",
    "field": "#ffffff",
    "pill": "#efefef",
    "pill_text": "#3a3a3a",
    "button": "#f4f4f4",
    "button_text": "#1c1c1c",
    "off": "#f7f7f7",
    "off_text": "#8d8d8d",
}
DARK = {
    "page": "#121212",
    "title": "#2a2a2a",
    "title_line": "#3a3a3a",
    "text": "#f3f3f3",
    "muted": "#b5b5b5",
    "body": "#1c1c1c",
    "box": "#3a3a3a",
    "field": "#262626",
    "pill": "#2e2e2e",
    "pill_text": "#d7d7d7",
    "button": "#2e2e2e",
    "button_text": "#f3f3f3",
    "off": "#242424",
    "off_text": "#8d8d8d",
}

FONT = "Segoe UI"
DECK_CONFIGS = Path.home() / ".local/share/Steam/steamapps/common/Steam Controller Configs"


def windows_light():
    """Windows theme when the registry can be read. Otherwise dark, for the Deck."""
    try:
        out = subprocess.run(
            ["cmd.exe", "/c", "reg", "query", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "/v", "AppsUseLightTheme"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode != 0:
            return False
        return "0x1" in out.stdout
    except (OSError, subprocess.TimeoutExpired):
        return False


def _row_summary(row):
    """Short 'Control · Binding' line for a shortcut row."""
    control = row.get("control", "")
    action = row.get("action", "")
    if action == "Keyboard":
        key = row.get("key", "")
        second = row.get("and", "none")
        binding = key if second in ("", "none") else f"{second} + {key}"
    elif action == "Run script":
        binding = row.get("command", "") or row.get("hotkey", "")
    elif action == "Mouse button":
        binding = row.get("mouse", "")
    elif action == "Mouse wheel":
        binding = row.get("wheel", "")
    elif action == "Gamepad button":
        binding = row.get("pad", "")
    else:
        binding = action
    return f"{control} \u00b7 {binding}" if binding else control


def _detect_folder():
    saved = library.load_folder()
    if saved:
        return saved
    if DECK_CONFIGS.is_dir():
        hits = [
            p / "config" / "413080"
            for p in DECK_CONFIGS.iterdir()
            if p.is_dir() and p.name.isdigit() and (p / "config" / "413080" / layout.TARGET_NAME).is_file()
        ]
        if len(hits) == 1:
            return str(hits[0])
    return ""


def _steam_running():
    if os.name != "posix":
        return False
    try:
        out = subprocess.run(["pgrep", "-x", "steam"], capture_output=True, timeout=2)
        return out.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _summon_keyboard(_event=None):
    if os.name != "posix":
        return
    try:
        subprocess.Popen(["steam", "steam://open/keyboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


class DeckApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.colors = LIGHT if windows_light() else DARK
        self.configure(bg=self.colors["body"])
        self.title("Deck Controls")
        self.geometry("1280x800")
        self.minsize(800, 640)
        self.rows = library.load()
        self.folder = ""
        self.index = None
        self._writing = False
        self._update_sha = ""
        self._update_checked = False
        self.status = tk.StringVar()
        self._build_list()
        self._build_detail()
        self._set_folder(_detect_folder(), save=False)
        self.show_list()

    def _build_list(self):
        c = self.colors
        self.list_frame = tk.Frame(self, bg=c["body"])
        bar = tk.Frame(self.list_frame, bg=c["title"], height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Deck Controls", bg=c["title"], fg=c["text"], font=(FONT, 20, "bold")).pack(side="left", padx=24)
        self.update_button = tk.Button(
            bar, text="Update ready", command=self.apply_update,
            bg=c["button"], fg=c["button_text"], relief="solid", bd=1,
            font=(FONT, 15, "bold"), padx=14, pady=6,
        )
        body = tk.Frame(self.list_frame, bg=c["body"], padx=24, pady=24)
        body.pack(fill="both", expand=True)
        tk.Label(
            body,
            text="Pick one, then write the file.",
            bg=c["body"], fg=c["text"], font=(FONT, 18), wraplength=1200, justify="left",
        ).pack(anchor="w", pady=(0, 16))
        folder = tk.Frame(body, bg=c["body"])
        folder.pack(fill="x", pady=(0, 16))
        tk.Label(folder, text="Folder", bg=c["body"], fg=c["text"], font=(FONT, 18), width=8, anchor="w").pack(side="left")
        self.path = tk.Label(
            folder, text="No folder chosen", bg=c["field"], fg=c["text"],
            font=(FONT, 18), anchor="w", padx=14, relief="solid", bd=1,
        )
        self.path.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=12)
        tk.Button(
            folder, text="Choose folder", command=self.choose_folder,
            bg=c["button"], fg=c["button_text"], relief="solid", bd=1,
            font=(FONT, 18), padx=16, pady=8,
        ).pack(side="left")

        list_wrap = tk.Frame(body, bg=c["body"], highlightthickness=1, highlightbackground=c["box"])
        list_wrap.pack(fill="both", expand=True)
        header = tk.Frame(list_wrap, bg=c["title"], height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, minsize=150)
        header.columnconfigure(2, minsize=80)
        header.columnconfigure(3, minsize=110)
        tk.Label(header, text="Name", bg=c["title"], fg=c["muted"], font=(FONT, 14, "bold"), anchor="w", padx=16).grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="Type", bg=c["title"], fg=c["muted"], font=(FONT, 14, "bold")).grid(row=0, column=1)
        tk.Label(header, text="On", bg=c["title"], fg=c["muted"], font=(FONT, 14, "bold")).grid(row=0, column=2)
        tk.Label(header, text="Select", bg=c["title"], fg=c["muted"], font=(FONT, 14, "bold")).grid(row=0, column=3)

        self.canvas = tk.Canvas(list_wrap, bg=c["body"], highlightthickness=0, height=320)
        self.canvas.pack(fill="both", expand=True)
        self.rows_frame = tk.Frame(self.canvas, bg=c["body"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.rows_frame.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        self._drag_y = None
        self._drag_top = 0.0
        self._bind_scroll(self.canvas)
        self._bind_scroll(self.rows_frame)

        actions = tk.Frame(body, bg=c["body"])
        actions.pack(fill="x", pady=(16, 0))
        tk.Button(
            actions, text="Add shortcut", command=self.add_row,
            bg=c["button"], fg=c["button_text"], relief="solid", bd=1,
            font=(FONT, 18), padx=16, pady=10,
        ).pack(side="left", padx=(0, 12))
        self.restore_button = tk.Button(
            actions, text="Restore", command=self.restore,
            bg=c["off"], fg=c["off_text"], relief="solid", bd=1,
            font=(FONT, 18), padx=16, pady=10,
        )
        self.restore_button.pack(side="left", padx=(0, 12))
        self.write_button = tk.Button(
            actions, text="Write", command=self.write,
            bg=c["off"], fg=c["off_text"], relief="solid", bd=1,
            font=(FONT, 18), padx=16, pady=10,
        )
        self.write_button.pack(side="left", fill="x", expand=True)
        tk.Label(
            body, textvariable=self.status, bg=c["body"], fg=c["muted"],
            font=(FONT, 16), wraplength=1200, justify="left",
        ).pack(anchor="w", pady=(10, 0))

    def _bind_scroll(self, widget):
        widget.bind("<ButtonPress-1>", self._drag_start)
        widget.bind("<B1-Motion>", self._drag_move)
        widget.bind("<MouseWheel>", self._on_wheel)
        widget.bind("<Button-4>", lambda _e: self.canvas.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda _e: self.canvas.yview_scroll(1, "units"))

    def _drag_start(self, event):
        self._drag_y = event.y_root
        self._drag_top = self.canvas.yview()[0]

    def _drag_move(self, event):
        if self._drag_y is None:
            return
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        total = bbox[3] - bbox[1]
        visible = self.canvas.winfo_height()
        if total <= visible:
            return
        dy = self._drag_y - event.y_root
        frac = self._drag_top + (dy / total)
        max_top = max(0.0, 1.0 - (visible / total))
        self.canvas.yview_moveto(min(max(0.0, frac), max_top))

    def _on_wheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_detail(self):
        c = self.colors
        self.detail = tk.Frame(self, bg=c["body"])
        bar = tk.Frame(self.detail, bg=c["title"], height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Button(
            bar, text="Back", command=self.back, bg=c["title"], fg=c["text"],
            relief="flat", bd=0, font=(FONT, 18), padx=12, pady=8,
        ).pack(side="left", padx=8)
        self.detail_title = tk.Label(bar, text="", bg=c["title"], fg=c["text"], font=(FONT, 20, "bold"))
        self.detail_title.pack(side="left")
        form = tk.Frame(self.detail, bg=c["body"], padx=24, pady=24)
        form.pack(fill="both", expand=True)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        self.form = form
        self.fields = {}
        self._field(form, "Name", "name", kind="entry")
        self._field(form, "Control", "control", values=library.CONTROLS)
        self._field(form, "Action", "action", values=library.ACTIONS, command=self._sync_fields)
        self._field(form, "Key", "key", values=library.KEYS)
        self._field(form, "And", "and", values=library.ANDS)
        self._field(form, "Command", "command", kind="entry")
        self._field(form, "Hotkey", "hotkey", values=library.HOTKEYS)
        self._field(form, "Button", "mouse", values=library.MICE)
        self._field(form, "Wheel", "wheel", values=library.WHEELS)
        self._field(form, "Pad", "pad", values=library.PADS)
        self.remove_button = tk.Button(
            form, text="Remove", command=self.remove_row,
            bg=c["button"], fg=c["button_text"], relief="solid", bd=1,
            font=(FONT, 18), padx=16, pady=10,
        )

    def _field(self, parent, label, key, kind="menu", values=(), command=None):
        c = self.colors
        frame = tk.Frame(parent, bg=c["body"])
        tk.Label(frame, text=label, bg=c["body"], fg=c["muted"], font=(FONT, 14)).pack(anchor="w")
        var = tk.StringVar()
        if kind == "entry":
            widget = tk.Entry(frame, textvariable=var, bg=c["field"], fg=c["text"], relief="solid", bd=1, font=(FONT, 18))
            widget.bind("<FocusIn>", _summon_keyboard)
            widget.pack(fill="x", ipady=12, pady=(6, 16))
        else:
            widget = tk.OptionMenu(frame, var, *values, command=command)
            widget.configure(
                bg=c["button"], fg=c["button_text"], highlightthickness=1,
                font=(FONT, 18), anchor="w",
            )
            widget["menu"].configure(font=(FONT, 18))
            widget.pack(fill="x", pady=(6, 16), ipady=8)
        self.fields[key] = (frame, var)

    def show_list(self):
        self.detail.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        self._fill_rows()
        self._refresh_write()
        self._check_update()

    def _fill_rows(self):
        c = self.colors
        for child in self.rows_frame.winfo_children():
            child.destroy()
        for index, row in enumerate(self.rows):
            enabled = row.get("enabled", True)
            line = tk.Frame(self.rows_frame, bg=c["body"], height=68)
            line.pack(fill="x")
            line.pack_propagate(False)
            line.columnconfigure(0, weight=1)
            line.columnconfigure(1, minsize=150)
            line.columnconfigure(2, minsize=80)
            line.columnconfigure(3, minsize=110)
            left = tk.Frame(line, bg=c["body"])
            left.grid(row=0, column=0, sticky="ew", padx=(16, 8))
            name = tk.Label(
                left, text=row["name"], bg=c["body"],
                fg=c["text"] if enabled else c["muted"],
                font=(FONT, 18, "bold"), anchor="w",
            )
            name.pack(fill="x")
            sub = tk.Label(left, text=_row_summary(row), bg=c["body"], fg=c["muted"], font=(FONT, 13), anchor="w")
            sub.pack(fill="x")
            kind = tk.Label(line, text=library.kind_of(row["action"]), bg=c["pill"], fg=c["pill_text"], font=(FONT, 14), padx=12, pady=4)
            kind.grid(row=0, column=1)
            toggle_btn = tk.Button(
                line, text="On" if enabled else "Off",
                command=lambda i=index: self.toggle_row(i),
                bg=c["button"] if enabled else c["off"],
                fg=c["button_text"] if enabled else c["off_text"],
                relief="solid", bd=1, font=(FONT, 14), padx=10, pady=6,
            )
            toggle_btn.grid(row=0, column=2, padx=4)
            select_btn = tk.Button(
                line, text="Select", command=lambda i=index: self.open_row(i),
                bg=c["button"], fg=c["button_text"], relief="solid", bd=1,
                font=(FONT, 15), padx=14, pady=6,
            )
            select_btn.grid(row=0, column=3, padx=(4, 16))
            for widget in (line, left, name, sub, kind):
                self._bind_scroll(widget)

    def toggle_row(self, index):
        row = self.rows[index]
        row["enabled"] = not row.get("enabled", True)
        library.save(self.rows)
        self._fill_rows()
        self._refresh_write()

    def open_row(self, index):
        self.index = index
        row = self.rows[index]
        self.detail_title.configure(text=row["name"] or "Shortcut")
        for key, (_frame, var) in self.fields.items():
            var.set(row.get(key, ""))
        self.list_frame.pack_forget()
        self.detail.pack(fill="both", expand=True)
        self._sync_fields()

    def _sync_fields(self, _value=None):
        action = self.fields["action"][1].get()
        layout_rows = [
            ("name", None),
            ("control", "action"),
        ]
        if action == "Keyboard":
            layout_rows.append(("key", "and"))
        elif action == "Run script":
            layout_rows.append(("command", "hotkey"))
        elif action == "Mouse button":
            layout_rows.append(("mouse", None))
        elif action == "Mouse wheel":
            layout_rows.append(("wheel", None))
        elif action == "Gamepad button":
            layout_rows.append(("pad", None))

        self.remove_button.grid_forget()
        for frame, _var in self.fields.values():
            frame.grid_forget()

        for row_idx, (left_key, right_key) in enumerate(layout_rows):
            if right_key is None:
                self.fields[left_key][0].grid(row=row_idx, column=0, columnspan=2, sticky="ew")
            else:
                self.fields[left_key][0].grid(row=row_idx, column=0, sticky="ew", padx=(0, 8))
                self.fields[right_key][0].grid(row=row_idx, column=1, sticky="ew", padx=(8, 0))
        self.remove_button.grid(row=len(layout_rows), column=0, sticky="w", pady=(8, 0))

    def _store(self):
        if self.index is None:
            return
        row = self.rows[self.index]
        for key, (_frame, var) in self.fields.items():
            row[key] = var.get()
        library.save(self.rows)

    def back(self):
        self._store()
        self.index = None
        self.show_list()

    def add_row(self):
        self.rows.append(library.blank())
        library.save(self.rows)
        self.open_row(len(self.rows) - 1)

    def remove_row(self):
        if self.index is None:
            return
        del self.rows[self.index]
        library.save(self.rows)
        self.index = None
        self.show_list()

    def _set_folder(self, chosen, save=True):
        if not chosen:
            return
        self.folder = chosen
        if save:
            library.save_folder(chosen)
        shown = chosen
        if len(shown) > 64:
            shown = shown[:20] + "..." + shown[-36:]
        self.path.configure(text=shown)

    def choose_folder(self):
        if self.folder and Path(self.folder).is_dir():
            start = self.folder
        elif DECK_CONFIGS.is_dir():
            start = str(DECK_CONFIGS)
        elif Path("/mnt/c").is_dir():
            start = "/mnt"
        else:
            start = str(Path.home())
        chosen = filedialog.askdirectory(initialdir=start, parent=self)
        if not chosen:
            return
        self._set_folder(chosen, save=True)
        self._refresh_write()

    def _paint_write(self, can_write):
        # Stay clickable. A disabled Tk button ignores the click.
        if can_write:
            self.write_button.configure(state="normal", bg=self.colors["button"], fg=self.colors["button_text"])
        else:
            self.write_button.configure(state="normal", bg=self.colors["off"], fg=self.colors["off_text"])
        has_backup = layout.latest_backup(self.folder) is not None
        if has_backup:
            self.restore_button.configure(state="normal", bg=self.colors["button"], fg=self.colors["button_text"])
        else:
            self.restore_button.configure(state="normal", bg=self.colors["off"], fg=self.colors["off_text"])

    def _refresh_write(self):
        status, can_write = layout.assess(self.folder, self.rows)
        self.status.set(status)
        self._paint_write(can_write)

    def restore(self):
        if self._writing:
            return
        backup = layout.latest_backup(self.folder)
        if backup is None:
            messagebox.showinfo("Restore", "No backup found in this folder.", parent=self)
            return
        if not messagebox.askyesno(
            "Restore",
            "Restore %s over %s?" % (backup.name, layout.TARGET_NAME),
            parent=self,
        ):
            return
        if _steam_running() and not messagebox.askyesno(
            "Steam is running",
            "Steam is open and may overwrite this file.\n\nRestore anyway?",
            parent=self,
        ):
            return
        message, _restored = layout.restore_backup(self.folder)
        self.status.set(message)
        messagebox.showinfo("Restore", message, parent=self)
        _status, can_write = layout.assess(self.folder, self.rows)
        self._paint_write(can_write)

    def write(self):
        if self._writing:
            return
        try:
            status, can_write = layout.assess(self.folder, self.rows)
        except Exception as exc:
            messagebox.showinfo("Write", "Could not write. %s" % exc, parent=self)
            return
        if not can_write:
            self.status.set(status)
            messagebox.showinfo("Write", status, parent=self)
            return
        if _steam_running() and not messagebox.askyesno(
            "Steam is running",
            "Steam is open and may overwrite this file.\n\nWrite anyway?",
            parent=self,
        ):
            return
        self._writing = True
        self.write_button.configure(state="disabled", bg=self.colors["off"], fg=self.colors["off_text"])
        self.status.set("Backing up the current file.")
        self.update_idletasks()
        try:
            message, wrote = layout.apply_folder(self.folder, self.rows)
        except Exception as exc:
            message, wrote = "Could not write. %s" % exc, False
        self._writing = False
        self.status.set(message)
        messagebox.showinfo("Write", message, parent=self)
        _status, can_write = layout.assess(self.folder, self.rows)
        self._paint_write(can_write)

    def _check_update(self):
        if self._update_checked or not update.REPO:
            return
        self._update_checked = True
        folder = Path(__file__).resolve().parent

        def work():
            try:
                message, ready, sha = update.available(folder, update.fetch)
            except Exception:
                message, ready, sha = "Could not check for updates.", False, ""
            self.after(0, lambda m=message, r=ready, s=sha: self._update_ready(m, r, s))

        threading.Thread(target=work, daemon=True).start()

    def _update_ready(self, message, ready, sha):
        if not ready:
            return
        self._update_sha = sha
        self.update_button.pack(side="right", padx=16)

    def apply_update(self):
        if not self._update_sha:
            return
        if not messagebox.askyesno(
            "Update",
            "Replace the app with the copy from GitHub? Your shortcuts stay.",
            parent=self,
        ):
            return
        sha = self._update_sha
        folder = Path(__file__).resolve().parent
        self.update_button.configure(state="disabled")

        def work():
            try:
                blob, reason = update.download(update.REPO, sha, update.fetch)
                if blob is None:
                    result = (reason, False)
                else:
                    files, reason = update.files_from_zip(blob)
                    if files is None:
                        result = (reason, False)
                    else:
                        result = update.apply_files(folder, files, sha)
            except Exception as exc:
                result = ("Could not update. %s" % exc, False)
            self.after(0, lambda r=result: self._update_done(r))

        threading.Thread(target=work, daemon=True).start()

    def _update_done(self, result):
        message, applied = result
        self.update_button.configure(state="normal")
        if applied:
            self.update_button.pack_forget()
            self._update_sha = ""
        messagebox.showinfo("Update", message, parent=self)


if __name__ == "__main__":
    DeckApp().mainloop()

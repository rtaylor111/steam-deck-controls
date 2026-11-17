"""Shortcuts window. List, then the breakdown for one shortcut."""

import tkinter as tk
from tkinter import filedialog, messagebox

import library
import layout

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
    "button": "#f4f4f4",
    "off": "#8d8d8d",
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
    "button": "#2e2e2e",
    "off": "#8d8d8d",
}


def windows_light():
    try:
        import subprocess
        out = subprocess.run(
            ["cmd.exe", "/c", "reg", "query", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "/v", "AppsUseLightTheme"],
            capture_output=True, text=True, timeout=5,
        )
        return "0x1" in out.stdout
    except (OSError, subprocess.TimeoutExpired):
        return True


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.colors = LIGHT if windows_light() else DARK
        self.configure(bg=self.colors["body"])
        self.title("Shortcuts")
        self.geometry("440x640")
        self.minsize(360, 480)
        self.rows = library.load()
        self.folder = ""
        self.index = None
        self._writing = False
        self.status = tk.StringVar()
        self._build_list()
        self._build_detail()
        self.show_list()

    def _build_list(self):
        c = self.colors
        self.list_frame = tk.Frame(self, bg=c["body"])
        bar = tk.Frame(self.list_frame, bg=c["title"], height=44)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Shortcuts", bg=c["title"], fg=c["text"], font=("Segoe UI", 12, "bold")).pack(side="left", padx=14)
        body = tk.Frame(self.list_frame, bg=c["body"], padx=16, pady=16)
        body.pack(fill="both", expand=True)
        tk.Label(
            body,
            text="Saves each named shortcut, then writes it into the layout file.",
            bg=c["body"], fg=c["text"], font=("Segoe UI", 11), wraplength=390, justify="left",
        ).pack(anchor="w", pady=(0, 12))
        folder = tk.Frame(body, bg=c["body"])
        folder.pack(fill="x", pady=(0, 12))
        tk.Label(folder, text="Folder", bg=c["body"], fg=c["text"], font=("Segoe UI", 11), width=8, anchor="w").pack(side="left")
        self.path = tk.Label(folder, text="No folder chosen", bg=c["field"], fg=c["text"], font=("Segoe UI", 10), anchor="w", padx=8, relief="solid", bd=1)
        self.path.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=6)
        tk.Button(folder, text="Choose folder", command=self.choose_folder, bg=c["button"], fg=c["text"], relief="solid", bd=1).pack(side="left")
        self.canvas = tk.Canvas(body, bg=c["body"], highlightthickness=1, highlightbackground=c["box"], height=260)
        self.canvas.pack(fill="both", expand=True)
        self.rows_frame = tk.Frame(self.canvas, bg=c["body"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.rows_frame.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        tk.Button(body, text="Add shortcut", command=self.add_row, bg=c["button"], fg=c["text"], relief="solid", bd=1).pack(anchor="w", pady=(12, 0))
        self.write_button = tk.Button(body, text="Write", command=self.write, bg=c["button"], fg=c["off"], relief="solid", bd=1)
        self.write_button.pack(anchor="w", pady=(8, 0))
        tk.Label(body, textvariable=self.status, bg=c["body"], fg=c["muted"], font=("Segoe UI", 10), wraplength=390, justify="left").pack(anchor="w", pady=(8, 0))

    def _build_detail(self):
        c = self.colors
        self.detail = tk.Frame(self, bg=c["body"])
        bar = tk.Frame(self.detail, bg=c["title"], height=44)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Button(bar, text="Back", command=self.back, bg=c["title"], fg=c["text"], relief="flat", bd=0).pack(side="left", padx=6)
        self.detail_title = tk.Label(bar, text="", bg=c["title"], fg=c["text"], font=("Segoe UI", 12, "bold"))
        self.detail_title.pack(side="left")
        form = tk.Frame(self.detail, bg=c["body"], padx=16, pady=16)
        form.pack(fill="both", expand=True)
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
        self.remove_button = tk.Button(form, text="Remove", command=self.remove_row, bg=c["button"], fg=c["text"], relief="solid", bd=1)
        self.remove_button.pack(anchor="w", pady=(4, 0))

    def _field(self, parent, label, key, kind="menu", values=(), command=None):
        c = self.colors
        frame = tk.Frame(parent, bg=c["body"])
        tk.Label(frame, text=label, bg=c["body"], fg=c["muted"], font=("Segoe UI", 9)).pack(anchor="w")
        var = tk.StringVar()
        if kind == "entry":
            widget = tk.Entry(frame, textvariable=var, bg=c["field"], fg=c["text"], relief="solid", bd=1, font=("Segoe UI", 11))
            widget.pack(fill="x", ipady=4, pady=(2, 10))
        else:
            widget = tk.OptionMenu(frame, var, *values, command=command)
            widget.configure(bg=c["button"], fg=c["text"], highlightthickness=1, font=("Segoe UI", 10))
            widget.pack(fill="x", pady=(2, 10))
        self.fields[key] = (frame, var)

    def show_list(self):
        self.detail.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        self._fill_rows()
        self._refresh_write()

    def _fill_rows(self):
        c = self.colors
        for child in self.rows_frame.winfo_children():
            child.destroy()
        for index, row in enumerate(self.rows):
            line = tk.Frame(self.rows_frame, bg=c["body"])
            line.pack(fill="x")
            name = tk.Label(line, text=row["name"], bg=c["body"], fg=c["text"], font=("Segoe UI", 11, "bold"), anchor="w", padx=12, pady=12)
            name.pack(side="left", fill="x", expand=True)
            kind = tk.Label(line, text=library.kind_of(row["action"]), bg=c["pill"], fg=c["text"], font=("Segoe UI", 9), padx=8)
            kind.pack(side="right", padx=12)
            for widget in (line, name, kind):
                widget.bind("<Button-1>", lambda _e, i=index: self.open_row(i))

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
        show = {"name", "control", "action"}
        if action == "Keyboard":
            show.update({"key", "and"})
        elif action == "Run script":
            show.update({"command", "hotkey"})
        elif action == "Mouse button":
            show.add("mouse")
        elif action == "Mouse wheel":
            show.add("wheel")
        elif action == "Gamepad button":
            show.add("pad")
        self.remove_button.pack_forget()
        for key, (frame, _var) in self.fields.items():
            frame.pack_forget()
            if key in show:
                frame.pack(fill="x")
        self.remove_button.pack(anchor="w", pady=(4, 0))

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

    def choose_folder(self):
        chosen = filedialog.askdirectory(initialdir="/mnt", parent=self)
        if not chosen:
            return
        self.folder = chosen
        shown = chosen
        if len(shown) > 42:
            shown = shown[:12] + "..." + shown[-24:]
        self.path.configure(text=shown)
        self._refresh_write()

    def _paint_write(self, can_write):
        # Stay clickable. A disabled Tk button ignores the click.
        if can_write:
            self.write_button.configure(state="normal", fg=self.colors["text"])
        else:
            self.write_button.configure(state="normal", fg=self.colors["off"])

    def _refresh_write(self):
        status, can_write = layout.assess(self.folder, self.rows)
        self.status.set(status)
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
        self._writing = True
        self.write_button.configure(state="disabled", fg=self.colors["off"])
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


if __name__ == "__main__":
    App().mainloop()

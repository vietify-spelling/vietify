"""Minimal Tkinter GUI for vietify.

Run with ``vietify-gui`` or ``python -m vietify.gui``. Drag-and-drop of input
files needs the optional ``tkinterdnd2`` package (``pip install -e ".[gui]"``);
without it, use the Browse button.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .main import (
    LANGUAGE_CHOICES,
    process_text_file,
    text_to_vietify,
    text_to_vietify_all,
)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None


# (label shown in the list, value used for conversion)
MODES = (
    ("IPA + strong + weak (default)", "all"),
    ("weak", "weak"),
    ("strong", "strong"),
    ("ipa", "ipa"),
)
LABELS = {"weak": "Weak", "strong": "Strong", "ipa": "IPA"}


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.input_file: Path | None = None
        self.output_file: Path | None = None
        self.jobs: queue.Queue = queue.Queue()

        root.title("Vietify")
        root.geometry("680x760")
        root.columnconfigure(0, weight=1)

        pad = {"padx": 12, "pady": 4}

        # Text input
        ttk.Label(root, text="Text to convert").grid(row=0, column=0, sticky="w", **pad)
        self.text = tk.Text(root, height=6, wrap="word")
        self.text.grid(row=1, column=0, sticky="nsew", **pad)
        self.text.bind("<Control-Return>", lambda _event: self.convert())
        self._enable_drop(self.text)

        # File input (drag here or browse)
        file_frame = ttk.Frame(root)
        file_frame.grid(row=2, column=0, sticky="ew", **pad)
        file_frame.columnconfigure(0, weight=1)
        hint = (
            "Drop a text file here, or use Browse"
            if DND_FILES
            else "Browse for a text file (drag & drop needs tkinterdnd2)"
        )
        self.drop_label = tk.Label(
            file_frame, text=hint, relief="groove", padx=8, pady=8, anchor="w"
        )
        self.drop_label.grid(row=0, column=0, sticky="ew")
        self._enable_drop(self.drop_label)
        ttk.Button(file_frame, text="Browse…", command=self.browse_input).grid(
            row=0, column=1, padx=(6, 0)
        )
        ttk.Button(file_frame, text="Clear", command=self.clear_input).grid(
            row=0, column=2, padx=(6, 0)
        )

        # Options: scrollable language list and mode list
        options = ttk.Frame(root)
        options.grid(row=3, column=0, sticky="ew", **pad)
        options.columnconfigure((0, 1), weight=1)

        ttk.Label(options, text="Language").grid(row=0, column=0, sticky="w")
        ttk.Label(options, text="Output mode").grid(row=0, column=1, sticky="w")
        self.language_list = self._scroll_list(options, LANGUAGE_CHOICES, 0, "en-us")
        self.mode_list = self._scroll_list(
            options, [label for label, _ in MODES], 1, MODES[0][0]
        )

        # Output file and convert
        actions = ttk.Frame(root)
        actions.grid(row=4, column=0, sticky="ew", **pad)
        actions.columnconfigure(1, weight=1)
        ttk.Button(actions, text="Output file…", command=self.choose_output).grid(row=0, column=0)
        self.output_label = ttk.Label(actions, text="(not set)", anchor="w")
        self.output_label.grid(row=0, column=1, sticky="ew", padx=6)
        self.convert_button = ttk.Button(actions, text="Convert  (Ctrl+Enter)", command=self.convert)
        self.convert_button.grid(row=0, column=2)

        # Results
        self.results = ttk.Frame(root)
        self.results.grid(row=5, column=0, sticky="nsew", **pad)
        self.results.columnconfigure(0, weight=1)
        root.rowconfigure(5, weight=1)

        self.status = tk.StringVar(value="Paste text, or drop/browse a file.")
        ttk.Label(root, textvariable=self.status, anchor="w").grid(
            row=6, column=0, sticky="ew", padx=12, pady=(0, 8)
        )

        self.root.after(50, self._poll_jobs)

    # ----- widget helpers -------------------------------------------------

    def _scroll_list(
        self, parent: ttk.Frame, items, column: int, default: str
    ) -> tk.Listbox:
        frame = ttk.Frame(parent)
        frame.grid(row=1, column=column, sticky="nsew", padx=(0, 6) if column == 0 else 0)
        listbox = tk.Listbox(frame, height=6, exportselection=False)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scroll.set)
        listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for item in items:
            listbox.insert("end", item)
        listbox.selection_set(list(items).index(default))
        listbox.see(list(items).index(default))
        return listbox

    def _enable_drop(self, widget: tk.Widget) -> None:
        if DND_FILES is None:
            return
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", self._on_drop)

    def _selected(self, listbox: tk.Listbox) -> int:
        selection = listbox.curselection()
        return selection[0] if selection else 0

    # ----- input and output ----------------------------------------------

    def _on_drop(self, event) -> None:
        files = self.root.tk.splitlist(event.data)
        if files:
            self.set_input(Path(files[0]))

    def browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose a UTF-8 text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*")],
        )
        if path:
            self.set_input(Path(path))

    def set_input(self, path: Path) -> None:
        self.input_file = path
        self.drop_label.configure(text=f"File: {path}")
        self.mode_list.configure(state="disabled")
        self.status.set("File input writes IPA, strong and weak, as the CLI does.")

    def clear_input(self) -> None:
        self.input_file = None
        self.drop_label.configure(
            text="Drop a text file here, or use Browse"
            if DND_FILES
            else "Browse for a text file (drag & drop needs tkinterdnd2)"
        )
        self.mode_list.configure(state="normal")
        self.status.set("Paste text, or drop/browse a file.")

    def choose_output(self) -> None:
        initial = (
            f"{self.input_file.stem}_vietify.txt" if self.input_file else "vietify.txt"
        )
        path = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".txt",
            initialfile=initial,
            initialdir=str(self.input_file.parent) if self.input_file else None,
        )
        if path:
            self.output_file = Path(path)
            self.output_label.configure(text=str(self.output_file))

    # ----- conversion -----------------------------------------------------

    def convert(self) -> None:
        language = LANGUAGE_CHOICES[self._selected(self.language_list)]

        if self.input_file is not None:
            if self.output_file is None:
                self.choose_output()
            if self.output_file is None:
                return
            source, output = self.input_file, self.output_file
            self._start(
                lambda: process_text_file(source, output, language),
                lambda _result: self.status.set(f"Wrote {output}"),
            )
            return

        text = self.text.get("1.0", "end").strip()
        if not text:
            self.status.set("Paste text, or drop/browse a file.")
            return

        mode = MODES[self._selected(self.mode_list)][1]
        if mode == "all":
            self._start(
                lambda: text_to_vietify_all(text, language),
                lambda rows: self.show_results(
                    [("IPA", rows[0]), ("Strong", rows[1]), ("Weak", rows[2])]
                ),
            )
        else:
            self._start(
                lambda: text_to_vietify(text, language, mode),
                lambda value: self.show_results([(LABELS[mode], value)]),
            )

    def _start(self, job, show) -> None:
        self.status.set("Working…")
        self.convert_button.state(["disabled"])

        def worker() -> None:
            try:
                result = job()
            except Exception as error:  # shown to the user, not raised
                self.jobs.put(lambda: self._finish_error(error))
            else:
                self.jobs.put(lambda: self._finish(show, result))

        threading.Thread(target=worker, daemon=True).start()

    def _finish(self, show, result) -> None:
        self.convert_button.state(["!disabled"])
        show(result)
        if self.input_file is None:
            self.status.set("Done.")

    def _finish_error(self, error: Exception) -> None:
        self.convert_button.state(["!disabled"])
        self.status.set("Failed.")
        messagebox.showwarning("Vietify", str(error))

    def _poll_jobs(self) -> None:
        while True:
            try:
                callback = self.jobs.get_nowait()
            except queue.Empty:
                break
            callback()
        self.root.after(50, self._poll_jobs)

    def show_results(self, rows: list[tuple[str, str]]) -> None:
        for child in self.results.winfo_children():
            child.destroy()

        for row, (label, value) in enumerate(rows):
            ttk.Label(self.results, text=label).grid(row=row * 2, column=0, sticky="w")
            lines = max(1, len(value) // 70 + 1)
            box = tk.Text(self.results, height=lines, wrap="word", borderwidth=1)
            box.insert("1.0", value)
            box.configure(state="disabled")
            box.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 8))


def main() -> int:
    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

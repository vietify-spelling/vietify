"""Minimal Tkinter GUI for vietify.

Run with ``vietify-gui`` or ``python -m vietify.gui``. Drag-and-drop of input
files needs the optional ``tkinterdnd2`` package (``pip install -e ".[gui]"``);
without it, use the Browse button. The speaker button needs espeak-ng.
"""

from __future__ import annotations

import queue
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkfont

from PIL import Image, ImageDraw, ImageTk

from .main import (
    LANGUAGE_CHOICES,
    process_text_file,
    text_to_vietify,
    text_to_vietify_all,
)
from .espeak_runtime import configure_espeak
from .tts import speak

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None


# Colors: white background, black text, one strong accent for actions.
BG = "#ffffff"
FG = "#111111"
MUTED = "#f0f2f5"
BORDER = "#c9ced6"
ACCENT = "#1f5eff"
ACCENT_HOVER = "#1446cc"
ACCENT_TEXT = "#ffffff"

# (label shown in the list, value used for conversion)
MODES = (
    ("IPA + strong + weak (default)", "all"),
    ("weak", "weak"),
    ("strong", "strong"),
    ("ipa", "ipa"),
)
LABELS = {"weak": "Weak", "strong": "Strong", "ipa": "IPA"}
UI_FONTS = ("Noto Sans", "Segoe UI", "DejaVu Sans", "Liberation Sans", "Helvetica")
MONO_FONTS = ("Noto Sans Mono", "DejaVu Sans Mono", "Consolas", "Courier New")
UI_SIZE = 15
DROP_HINT = "Drop a text file here, or use Browse"
NO_DND_HINT = "Browse for a text file (drag & drop needs tkinterdnd2)"


SPEAKER_SIZE = 56


def _speaker_image(playing: bool, hover: bool) -> ImageTk.PhotoImage:
    """Render the speaker (or stop) icon supersampled, so edges are smooth."""
    k = 4
    size = SPEAKER_SIZE * k
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (0, 0, size - 1, size - 1),
        radius=size // 5,
        fill=ACCENT_HOVER if hover else ACCENT,
    )
    if playing:
        draw.rounded_rectangle(
            (size * 0.32, size * 0.32, size * 0.68, size * 0.68),
            radius=size // 40,
            fill=ACCENT_TEXT,
        )
    else:
        draw.polygon(
            [
                (size * 0.22, size * 0.40),
                (size * 0.36, size * 0.40),
                (size * 0.54, size * 0.25),
                (size * 0.54, size * 0.75),
                (size * 0.36, size * 0.60),
                (size * 0.22, size * 0.60),
            ],
            fill=ACCENT_TEXT,
        )
        cx, cy = size * 0.54, size * 0.50
        for radius in (size * 0.17, size * 0.29):
            draw.arc(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                start=-45,
                end=45,
                fill=ACCENT_TEXT,
                width=int(size * 0.05),
            )
    small = img.resize((SPEAKER_SIZE, SPEAKER_SIZE), Image.LANCZOS)
    return ImageTk.PhotoImage(small)


class SpeakerButton(tk.Label):
    """Speaker icon button; shows a stop square while playing."""

    def __init__(self, parent: tk.Widget, command) -> None:
        self.images = {
            (playing, hover): _speaker_image(playing, hover)
            for playing in (False, True)
            for hover in (False, True)
        }
        self.command = command
        self.playing = False
        self.hover = False
        super().__init__(
            parent, image=self.images[(False, False)], bg=BG, bd=0, cursor="hand2"
        )
        self.bind("<Button-1>", lambda _event: self.command())
        self.bind("<Enter>", lambda _event: self._set_hover(True))
        self.bind("<Leave>", lambda _event: self._set_hover(False))

    def set_playing(self, playing: bool) -> None:
        self.playing = playing
        self._refresh()

    def _set_hover(self, hover: bool) -> None:
        self.hover = hover
        self._refresh()

    def _refresh(self) -> None:
        self.configure(image=self.images[(self.playing, self.hover)])


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.input_file: Path | None = None
        self.output_file: Path | None = None
        self.jobs: queue.Queue = queue.Queue()
        self.player: subprocess.Popen | None = None

        root.title("Vietify")
        root.geometry(f"{min(1040, root.winfo_screenwidth() - 80)}x{min(1160, root.winfo_screenheight() - 40)}")
        root.configure(bg=BG)
        root.columnconfigure(0, weight=1)
        self._fonts()
        self._style()

        pad = {"padx": 14, "pady": 5}

        # Text input, with the speaker button beside its label.
        header = ttk.Frame(root)
        header.grid(row=0, column=0, sticky="ew", **pad)
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Text to convert", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.speaker = SpeakerButton(header, self.toggle_speech)
        self.speaker.grid(row=0, column=1, sticky="e")

        self.text = tk.Text(root, height=6, wrap="word", **self._text_colors(self.ui))
        self.text.grid(row=1, column=0, sticky="nsew", **pad)
        self.text.bind("<Control-Return>", lambda _event: self.convert())
        self._enable_drop(self.text)

        # File input (drag here or browse)
        file_frame = ttk.Frame(root)
        file_frame.grid(row=2, column=0, sticky="ew", **pad)
        file_frame.columnconfigure(0, weight=1)
        self.drop_label = tk.Label(
            file_frame,
            text=DROP_HINT if DND_FILES else NO_DND_HINT,
            bg=MUTED,
            fg="#444444",
            padx=10,
            pady=9,
            anchor="w",
        )
        self.drop_label.grid(row=0, column=0, sticky="ew")
        self._enable_drop(self.drop_label)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(
            row=0, column=1, padx=(8, 0)
        )
        ttk.Button(file_frame, text="Clear", command=self.clear_input).grid(
            row=0, column=2, padx=(8, 0)
        )

        # Options: scrollable language list and output-mode list
        options = ttk.Frame(root)
        options.grid(row=3, column=0, sticky="ew", **pad)
        options.columnconfigure((0, 1), weight=1)

        ttk.Label(options, text="Language", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        ttk.Label(options, text="Output mode", style="Heading.TLabel").grid(
            row=0, column=1, sticky="w"
        )
        self.language_list = self._scroll_list(options, LANGUAGE_CHOICES, 0, "en-us")
        self.mode_list = self._scroll_list(
            options, [label for label, _ in MODES], 1, MODES[0][0]
        )

        # Output file and convert
        actions = ttk.Frame(root)
        actions.grid(row=4, column=0, sticky="ew", **pad)
        actions.columnconfigure(1, weight=1)
        ttk.Button(actions, text="Output file", command=self.choose_output).grid(row=0, column=0)
        self.output_label = ttk.Label(actions, text="(not set)", anchor="w")
        self.output_label.grid(row=0, column=1, sticky="ew", padx=8)
        self.convert_button = ttk.Button(
            actions,
            text="Convert  (Ctrl+Enter)",
            style="Accent.TButton",
            command=self.convert,
        )
        self.convert_button.grid(row=0, column=2)

        # Results
        self.results = ttk.Frame(root)
        self.results.grid(row=5, column=0, sticky="nsew", **pad)
        self.results.columnconfigure(0, weight=1)
        root.rowconfigure(5, weight=1)

        self.status = tk.StringVar(value="Paste text, or drop/browse a file.")
        ttk.Label(root, textvariable=self.status, style="Status.TLabel").grid(
            row=6, column=0, sticky="ew", padx=14, pady=(0, 10)
        )

        self.root.after(50, self._poll_jobs)

    # ----- styling --------------------------------------------------------

    def _fonts(self) -> None:
        """Named fonts sized for large screens; ttk and Tk widgets inherit them."""
        families = set(tkfont.families())
        ui_family = next((f for f in UI_FONTS if f in families), "TkDefaultFont")
        mono_family = next((f for f in MONO_FONTS if f in families), "TkFixedFont")
        self.ui = tkfont.Font(family=ui_family, size=UI_SIZE)
        self.ui_bold = tkfont.Font(family=ui_family, size=UI_SIZE, weight="bold")
        self.mono = tkfont.Font(family=mono_family, size=UI_SIZE)
        for name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(family=ui_family, size=UI_SIZE)
        tkfont.nametofont("TkFixedFont").configure(family=mono_family, size=UI_SIZE)

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, bordercolor=BORDER)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Heading.TLabel", font=self.ui_bold)
        style.configure("Status.TLabel", foreground="#333333")
        style.configure(
            "TButton",
            background=MUTED,
            foreground=FG,
            bordercolor=BORDER,
            focusthickness=0,
            padding=(12, 6),
            relief="flat",
        )
        style.map("TButton", background=[("active", BORDER)])
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground=ACCENT_TEXT,
            bordercolor=ACCENT,
            font=self.ui_bold,
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT_HOVER), ("disabled", BORDER)],
            foreground=[("disabled", "#777777")],
        )
        style.configure("Vertical.TScrollbar", background=MUTED, troughcolor=BG)

    def _text_colors(self, font: tkfont.Font) -> dict:
        return {
            "font": font,
            "bg": BG,
            "fg": FG,
            "insertbackground": FG,
            "selectbackground": ACCENT,
            "selectforeground": ACCENT_TEXT,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": BORDER,
            "highlightcolor": ACCENT,
            "padx": 8,
            "pady": 6,
        }

    # ----- widget helpers -------------------------------------------------

    def _scroll_list(
        self, parent: ttk.Frame, items, column: int, default: str
    ) -> tk.Listbox:
        frame = ttk.Frame(parent)
        frame.grid(row=1, column=column, sticky="nsew", padx=(0, 8 if column == 0 else 0))
        listbox = tk.Listbox(
            frame,
            height=7,
            font=self.ui,
            exportselection=False,
            bg=BG,
            fg=FG,
            selectbackground=ACCENT,
            selectforeground=ACCENT_TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            relief="flat",
            activestyle="none",
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scroll.set)
        listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        for item in items:
            listbox.insert("end", item)
        index = list(items).index(default)
        listbox.selection_set(index)
        listbox.see(index)
        return listbox

    def _enable_drop(self, widget: tk.Widget) -> None:
        if DND_FILES is None:
            return
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", self._on_drop)

    def _selected(self, listbox: tk.Listbox) -> int:
        selection = listbox.curselection()
        return selection[0] if selection else 0

    def _language(self) -> str:
        return LANGUAGE_CHOICES[self._selected(self.language_list)]

    # ----- text-to-speech -------------------------------------------------

    def toggle_speech(self) -> None:
        if self.player is not None and self.player.poll() is None:
            self.player.terminate()
            self._speech_stopped()
            return

        text = self.text.get("1.0", "end").strip()
        if not text:
            self.status.set("Paste text to hear it.")
            return

        language = self._language()
        try:
            self.player = speak(text, language)
        except (RuntimeError, ValueError) as error:
            self.status.set(str(error))
            return
        self.speaker.set_playing(True)
        self.status.set(f"Speaking ({language})…")

    def _speech_stopped(self) -> None:
        self.player = None
        self.speaker.set_playing(False)

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
        self.drop_label.configure(text=DROP_HINT if DND_FILES else NO_DND_HINT)
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
        language = self._language()

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
        if self.player is not None and self.player.poll() is not None:
            self._speech_stopped()
            self.status.set("Done.")
        self.root.after(50, self._poll_jobs)

    def show_results(self, rows: list[tuple[str, str]]) -> None:
        for child in self.results.winfo_children():
            child.destroy()

        for row, (label, value) in enumerate(rows):
            ttk.Label(self.results, text=label, style="Heading.TLabel").grid(
                row=row * 2, column=0, sticky="w"
            )
            lines = max(1, len(value) // 52 + 1)
            box = tk.Text(self.results, height=lines, wrap="word", **self._text_colors(self.mono))
            box.insert("1.0", value)
            box.configure(state="disabled")
            box.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(2, 10))


def main() -> int:
    configure_espeak()
    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Minimal Tkinter GUI for vietify.

Run with ``vietify-gui`` or ``python -m vietify.gui``. Drag-and-drop of input
files needs the optional ``tkinterdnd2`` package (``pip install -e ".[gui]"``);
without it, use the Browse button. The speaker button needs espeak-ng.
The interface is in Vietnamese by default and can be switched to English.
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

from .espeak_runtime import configure_espeak
from .gui_i18n import (
    DEFAULT_UI_LANGUAGE,
    LANGUAGE_NAMES,
    MODES,
    STRINGS,
    UI_LANGUAGES,
)
from .gui_icons import emoji_image, flag_image
from .main import (
    LANGUAGE_CHOICES,
    process_text_file,
    text_to_vietify,
    text_to_vietify_all,
)
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

UI_FONTS = ("Noto Sans", "Segoe UI", "DejaVu Sans", "Liberation Sans", "Helvetica")
MONO_FONTS = ("Noto Sans Mono", "DejaVu Sans Mono", "Consolas", "Courier New")
UI_SIZE = 15
EMOJI_SIZE = 30
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
        self.ui_language = tk.StringVar(value=DEFAULT_UI_LANGUAGE)
        self.status_key = ("ready", {})
        self.status_text: str | None = None
        self.last_rows: list[tuple[str, str]] = []

        root.title("Vietify")
        root.geometry(f"{min(1040, root.winfo_screenwidth() - 80)}x{min(1160, root.winfo_screenheight() - 40)}")
        root.configure(bg=BG)
        root.columnconfigure(0, weight=1)
        self._fonts()
        self._style()

        pad = {"padx": 14, "pady": 5}

        # Top bar: interface language menu (with flags).
        topbar = ttk.Frame(root)
        topbar.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 0))
        topbar.columnconfigure(0, weight=1)
        ttk.Label(topbar, text="Vietify", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.language_menu_button = ttk.Menubutton(topbar, compound="left")
        menu = tk.Menu(self.language_menu_button, tearoff=False, font=self.ui)
        for code, name in UI_LANGUAGES.items():
            menu.add_radiobutton(
                label=" " + name,
                image=flag_image(code),
                compound="left",
                variable=self.ui_language,
                value=code,
                command=self._apply_language,
            )
        self.language_menu_button["menu"] = menu
        self.language_menu_button.grid(row=0, column=1, sticky="e")

        # Text input, with the speaker button beside its label.
        header = ttk.Frame(root)
        header.grid(row=1, column=0, sticky="ew", **pad)
        header.columnconfigure(0, weight=1)
        self.text_heading = ttk.Label(header, style="Heading.TLabel")
        self.text_heading.grid(row=0, column=0, sticky="w")
        self.speaker = SpeakerButton(header, self.toggle_speech)
        self.speaker.grid(row=0, column=1, sticky="e")

        self.text = tk.Text(root, height=6, wrap="word", **self._text_colors(self.ui))
        self.text.grid(row=2, column=0, sticky="nsew", **pad)
        self.text.bind("<Control-Return>", lambda _event: self.convert())
        self._enable_drop(self.text)

        # File input (drag here or browse)
        file_frame = ttk.Frame(root)
        file_frame.grid(row=3, column=0, sticky="ew", **pad)
        file_frame.columnconfigure(0, weight=1)
        self.drop_label = tk.Label(
            file_frame, bg=MUTED, fg="#444444", padx=10, pady=9, anchor="w"
        )
        self.drop_label.grid(row=0, column=0, sticky="ew")
        self._enable_drop(self.drop_label)
        self.browse_button = ttk.Button(file_frame, command=self.browse_input)
        self.browse_button.grid(row=0, column=1, padx=(8, 0))
        self.clear_button = ttk.Button(file_frame, command=self.clear_input)
        self.clear_button.grid(row=0, column=2, padx=(8, 0))

        # Options: scrollable language list and output-mode list
        options = ttk.Frame(root)
        options.grid(row=4, column=0, sticky="ew", **pad)
        options.columnconfigure((0, 1), weight=1)
        self.language_heading = ttk.Label(options, style="Heading.TLabel")
        self.language_heading.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.mode_heading = ttk.Label(options, style="Heading.TLabel")
        self.mode_heading.grid(row=0, column=1, sticky="w")
        self.language_tree = self._scroll_tree(options, 0)
        self.mode_tree = self._scroll_tree(options, 1)

        # Output file and convert
        actions = ttk.Frame(root)
        actions.grid(row=5, column=0, sticky="ew", **pad)
        actions.columnconfigure(1, weight=1)
        self.output_button = ttk.Button(actions, command=self.choose_output)
        self.output_button.grid(row=0, column=0)
        self.output_label = ttk.Label(actions, anchor="w")
        self.output_label.grid(row=0, column=1, sticky="ew", padx=8)
        self.convert_button = ttk.Button(
            actions, style="Accent.TButton", command=self.convert
        )
        self.convert_button.grid(row=0, column=2)

        # Results
        self.results = ttk.Frame(root)
        self.results.grid(row=6, column=0, sticky="nsew", **pad)
        self.results.columnconfigure(0, weight=1)
        root.rowconfigure(6, weight=1)

        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, style="Status.TLabel").grid(
            row=7, column=0, sticky="ew", padx=14, pady=(0, 10)
        )

        self._apply_language()
        self.root.after(50, self._poll_jobs)

    # ----- translation ----------------------------------------------------

    def t(self, key: str, **values) -> str:
        return STRINGS[self.ui_language.get()][key].format(**values)

    def set_status(self, key: str, **values) -> None:
        """Show a translated status line; it is re-translated on language change."""
        self.status_key = (key, values)
        self.status_text = None
        self.status.set(self.t(key, **values))

    def set_status_text(self, text: str) -> None:
        self.status_text = text
        self.status.set(text)

    def _apply_language(self) -> None:
        """Re-label every widget in the selected interface language."""
        language = self.ui_language.get()
        self.language_menu_button.configure(
            text=" " + UI_LANGUAGES[language], image=flag_image(language)
        )
        self.text_heading.configure(text=self.t("text_heading"))
        self.browse_button.configure(text=self.t("browse"))
        self.clear_button.configure(text=self.t("clear"))
        self.language_heading.configure(text=self.t("language"))
        self.mode_heading.configure(text=self.t("output_mode"))
        self.output_button.configure(text=self.t("output_file"))
        self.convert_button.configure(text=self.t("convert"))
        self._refresh_file_labels()
        self._fill_languages()
        self._fill_modes()
        if self.last_rows:
            self.show_results(self.last_rows)
        if self.status_text is not None:
            self.status.set(self.status_text)
        else:
            key, values = self.status_key
            self.status.set(self.t(key, **values))

    def _refresh_file_labels(self) -> None:
        if self.input_file is not None:
            self.drop_label.configure(text=self.t("file_label", path=self.input_file))
        else:
            self.drop_label.configure(
                text=self.t("drop_hint" if DND_FILES else "no_dnd_hint")
            )
        if self.output_file is not None:
            self.output_label.configure(text=str(self.output_file))
        else:
            self.output_label.configure(text=self.t("not_set"))

    # ----- styling --------------------------------------------------------

    def _fonts(self) -> None:
        """Named fonts sized for large screens; ttk and Tk widgets inherit them."""
        families = set(tkfont.families())
        ui_family = next((f for f in UI_FONTS if f in families), "TkDefaultFont")
        mono_family = next((f for f in MONO_FONTS if f in families), "TkFixedFont")
        self.ui = tkfont.Font(family=ui_family, size=UI_SIZE)
        self.ui_bold = tkfont.Font(family=ui_family, size=UI_SIZE, weight="bold")
        self.title_font = tkfont.Font(family=ui_family, size=UI_SIZE + 5, weight="bold")
        self.mono = tkfont.Font(family=mono_family, size=UI_SIZE)
        for name in ("TkDefaultFont", "TkTextFont", "TkHeadingFont", "TkMenuFont"):
            tkfont.nametofont(name).configure(family=ui_family, size=UI_SIZE)
        tkfont.nametofont("TkFixedFont").configure(family=mono_family, size=UI_SIZE)

    def _style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, bordercolor=BORDER)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("Heading.TLabel", font=self.ui_bold)
        style.configure("Title.TLabel", font=self.title_font)
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
        style.configure(
            "TMenubutton",
            background=MUTED,
            foreground=FG,
            bordercolor=BORDER,
            padding=(12, 6),
            relief="flat",
        )
        style.map("TMenubutton", background=[("active", BORDER)])
        style.configure("Vertical.TScrollbar", background=MUTED, troughcolor=BG)
        style.configure(
            "Treeview",
            font=self.ui,
            rowheight=max(44, EMOJI_SIZE + 12),
            background=BG,
            fieldbackground=BG,
            foreground=FG,
            bordercolor=BORDER,
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", ACCENT_TEXT)],
        )
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

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

    def _scroll_tree(self, parent: ttk.Frame, column: int) -> ttk.Treeview:
        """A scrollable single-select list that can show an image beside each row."""
        frame = ttk.Frame(parent, borderwidth=1, relief="solid")
        frame.grid(row=1, column=column, sticky="nsew", padx=(0, 8 if column == 0 else 0))
        tree = ttk.Treeview(frame, show="tree", selectmode="browse", height=5)
        tree.column("#0", stretch=True)
        tree.tag_configure("disabled", foreground="#9aa0a6")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _fill_languages(self) -> None:
        tree = self.language_tree
        selected = tree.selection()[0] if tree.selection() else "en-us"
        names = LANGUAGE_NAMES[self.ui_language.get()]
        tree.delete(*tree.get_children())
        for code in LANGUAGE_CHOICES:
            tree.insert("", "end", iid=code, text=f"{names[code]}  ({code})")
        tree.selection_set(selected)
        tree.see(selected)

    def _fill_modes(self) -> None:
        tree = self.mode_tree
        selected = tree.selection()[0] if tree.selection() else "all"
        index = 2 if self.ui_language.get() == "vi" else 1
        tags = ("disabled",) if self.input_file is not None else ()
        tree.delete(*tree.get_children())
        for value, entry in MODES.items():
            tree.insert(
                "",
                "end",
                iid=value,
                text="  " + entry[index],
                image=emoji_image(entry[0], EMOJI_SIZE) or "",
                tags=tags,
            )
        tree.selection_set(selected)

    def _enable_drop(self, widget: tk.Widget) -> None:
        if DND_FILES is None:
            return
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", self._on_drop)

    def _language(self) -> str:
        selection = self.language_tree.selection()
        return selection[0] if selection else "en-us"

    def _mode(self) -> str:
        selection = self.mode_tree.selection()
        return selection[0] if selection else "all"

    # ----- text-to-speech -------------------------------------------------

    def toggle_speech(self) -> None:
        if self.player is not None and self.player.poll() is None:
            self.player.terminate()
            self._speech_stopped()
            return

        text = self.text.get("1.0", "end").strip()
        if not text:
            self.set_status("paste_to_hear")
            return

        language = self._language()
        try:
            self.player = speak(text, language)
        except (RuntimeError, ValueError) as error:
            self.set_status_text(str(error))
            return
        self.speaker.set_playing(True)
        self.set_status("speaking", language=language)

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
            title=self.t("open_title"),
            filetypes=[
                (self.t("text_files"), "*.txt"),
                (self.t("all_files"), "*"),
            ],
        )
        if path:
            self.set_input(Path(path))

    def set_input(self, path: Path) -> None:
        self.input_file = path
        self._refresh_file_labels()
        self.mode_tree.configure(selectmode="none")
        self._fill_modes()
        self.set_status("file_mode")

    def clear_input(self) -> None:
        self.input_file = None
        self._refresh_file_labels()
        self.mode_tree.configure(selectmode="browse")
        self._fill_modes()
        self.set_status("ready")

    def choose_output(self) -> None:
        initial = (
            f"{self.input_file.stem}_vietify.txt" if self.input_file else "vietify.txt"
        )
        path = filedialog.asksaveasfilename(
            title=self.t("save_title"),
            defaultextension=".txt",
            initialfile=initial,
            initialdir=str(self.input_file.parent) if self.input_file else None,
        )
        if path:
            self.output_file = Path(path)
            self._refresh_file_labels()

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
                lambda _result: self.set_status("wrote", path=output),
            )
            return

        text = self.text.get("1.0", "end").strip()
        if not text:
            self.set_status("ready")
            return

        mode = self._mode()
        if mode == "all":
            self._start(
                lambda: text_to_vietify_all(text, language),
                lambda rows: self.show_results(
                    [("ipa", rows[0]), ("strong", rows[1]), ("weak", rows[2])]
                ),
            )
        else:
            self._start(
                lambda: text_to_vietify(text, language, mode),
                lambda value: self.show_results([(mode, value)]),
            )

    def _start(self, job, show) -> None:
        self.set_status("working")
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
            self.set_status("done")

    def _finish_error(self, error: Exception) -> None:
        self.convert_button.state(["!disabled"])
        self.set_status("failed")
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
            self.set_status("done")
        self.root.after(50, self._poll_jobs)

    def show_results(self, rows: list[tuple[str, str]]) -> None:
        """Show result boxes. Each row is (mode key, text), headed by its emoji."""
        self.last_rows = rows
        for child in self.results.winfo_children():
            child.destroy()

        for row, (key, value) in enumerate(rows):
            heading = ttk.Label(
                self.results,
                text=" " + self.t(f"result_{key}"),
                image=emoji_image(MODES[key][0], 26) or "",
                compound="left",
                style="Heading.TLabel",
            )
            heading.grid(row=row * 2, column=0, sticky="w")
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

"""Interface text for the GUI in Vietnamese (default) and English."""

DEFAULT_UI_LANGUAGE = "vi"

# Names shown in the interface-language menu, always in their own language.
UI_LANGUAGES = {"vi": "Tiếng Việt", "en": "English"}

# Output modes: value -> (emoji, English label, Vietnamese label)
MODES = {
    "all": ("😊", "Default (all three results)", "Mặc định (cả ba kết quả)"),
    "weak": ("🤓", "Weak", "Sát"),
    "strong": ("🤪", "Strong", "Việt hóa mạnh"),
    "ipa": ("💯", "IPA", "IPA"),
}

# Input languages (the CLI language codes).
LANGUAGE_NAMES = {
    "en": {
        "en-gb": "English (UK)",
        "en-us": "English (US)",
        "en-au": "English (Australia)",
        "fr": "French",
        "de": "German",
        "ru": "Russian",
        "ch": "Chinese (pinyin)",
        "ja": "Japanese (Hepburn)",
        "ipa": "Input is IPA",
    },
    "vi": {
        "en-gb": "Tiếng Anh (Anh)",
        "en-us": "Tiếng Anh (Mỹ)",
        "en-au": "Tiếng Anh (Úc)",
        "fr": "Tiếng Pháp",
        "de": "Tiếng Đức",
        "ru": "Tiếng Nga",
        "ch": "Tiếng Trung (pinyin)",
        "ja": "Tiếng Nhật (Hepburn)",
        "ipa": "Đầu vào là IPA",
    },
}

STRINGS = {
    "en": {
        "text_heading": "Text to convert",
        "drop_hint": "Drop a text file here, or use Browse",
        "no_dnd_hint": "Browse for a text file (drag & drop needs tkinterdnd2)",
        "file_label": "File: {path}",
        "browse": "Browse",
        "clear": "Clear",
        "language": "Language",
        "output_mode": "Output mode",
        "output_file": "Output file",
        "not_set": "(not set)",
        "convert": "Convert  (Ctrl+Enter)",
        "ready": "Paste text, or drop/browse a file.",
        "file_mode": "File input writes IPA, strong and weak, as the CLI does.",
        "working": "Working…",
        "done": "Done.",
        "failed": "Failed.",
        "wrote": "Wrote {path}",
        "speaking": "Speaking ({language})…",
        "paste_to_hear": "Paste text to hear it.",
        "open_title": "Choose a UTF-8 text file",
        "save_title": "Save output as",
        "text_files": "Text files",
        "all_files": "All files",
        "result_ipa": "IPA",
        "result_strong": "Strong",
        "result_weak": "Weak",
    },
    "vi": {
        "text_heading": "Văn bản cần chuyển đổi",
        "drop_hint": "Thả tệp văn bản vào đây, hoặc bấm Chọn tệp",
        "no_dnd_hint": "Bấm Chọn tệp để mở tệp văn bản (kéo thả cần tkinterdnd2)",
        "file_label": "Tệp: {path}",
        "browse": "Chọn tệp",
        "clear": "Xóa",
        "language": "Ngôn ngữ",
        "output_mode": "Chế độ xuất",
        "output_file": "Tệp xuất",
        "not_set": "(chưa chọn)",
        "convert": "Chuyển đổi  (Ctrl+Enter)",
        "ready": "Dán văn bản, hoặc thả/chọn một tệp.",
        "file_mode": "Tệp đầu vào luôn xuất IPA, Việt hóa mạnh và Sát, giống dòng lệnh.",
        "working": "Đang xử lý…",
        "done": "Xong.",
        "failed": "Thất bại.",
        "wrote": "Đã ghi {path}",
        "speaking": "Đang đọc ({language})…",
        "paste_to_hear": "Dán văn bản để nghe.",
        "open_title": "Chọn tệp văn bản UTF-8",
        "save_title": "Lưu kết quả thành",
        "text_files": "Tệp văn bản",
        "all_files": "Tất cả tệp",
        "result_ipa": "IPA",
        "result_strong": "Việt hóa mạnh",
        "result_weak": "Sát",
    },
}

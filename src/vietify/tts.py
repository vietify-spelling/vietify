"""Text-to-speech through espeak-ng, using the same language codes as the CLI."""

from __future__ import annotations

import shutil
import subprocess

# CLI language code -> espeak-ng voice. "ipa" has no voice: espeak cannot read IPA.
VOICES: dict[str, str] = {
    "en-gb": "en-gb",
    "en-us": "en-us",
    "en-au": "en-au",
    "fr": "fr-fr",
    "de": "de",
    "ru": "ru",
    "ch": "cmn",
    "ja": "ja",
}


def espeak_binary() -> str | None:
    return shutil.which("espeak-ng") or shutil.which("espeak")


def speak(text: str, language: str) -> subprocess.Popen:
    """Start speaking text in the language's voice and return the process."""
    binary = espeak_binary()
    if binary is None:
        raise RuntimeError("espeak-ng is not installed")
    voice = VOICES.get(language)
    if voice is None:
        raise ValueError(f"no speech voice for language {language!r}")
    return subprocess.Popen([binary, "-v", voice, "--", text])

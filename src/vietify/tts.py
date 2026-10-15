"""Text-to-speech through espeak-ng, using the same language codes as the CLI."""

from __future__ import annotations

from .espeak_runtime import espeak_binary, espeak_data_args, espeak_env

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


def speak(text: str, language: str) -> subprocess.Popen:
    """Start speaking text in the language's voice and return the process."""
    binary = espeak_binary()
    if binary is None:
        raise RuntimeError("espeak-ng is not installed")
    voice = VOICES.get(language)
    if voice is None:
        raise ValueError(f"no speech voice for language {language!r}")
    command = [binary, *espeak_data_args(), "-v", voice, "--", text]
    return subprocess.Popen(command, env=espeak_env())

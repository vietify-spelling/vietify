"""Point espeak-ng at bundled files when running as a frozen (PyInstaller) app.

Layout inside a bundle (created by packaging/build.py):
    <bundle>/espeak/libespeak-ng.so.1      (or .dylib / .dll)
    <bundle>/espeak/espeak-ng[.exe]
    <bundle>/espeak/espeak-ng-data/
Outside a bundle, the system espeak-ng installation is used unchanged.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    LIBRARY_NAME = "libespeak-ng.dll"
    BINARY_NAME = "espeak-ng.exe"
elif sys.platform == "darwin":
    LIBRARY_NAME = "libespeak-ng.dylib"
    BINARY_NAME = "espeak-ng"
else:
    LIBRARY_NAME = "libespeak-ng.so.1"
    BINARY_NAME = "espeak-ng"


def bundled_dir() -> Path | None:
    """Return the bundled espeak folder, or None when not running frozen."""
    if not getattr(sys, "frozen", False):
        return None
    base = Path(getattr(sys, "_MEIPASS", "")) / "espeak"
    return base if base.is_dir() else None


def configure_espeak() -> None:
    """Tell phonemizer which espeak library and data to use."""
    base = bundled_dir()
    if base is None:
        return
    from phonemizer.backend.espeak.wrapper import EspeakWrapper

    EspeakWrapper.set_library(str(base / LIBRARY_NAME))
    EspeakWrapper.set_data_path(str(base / "espeak-ng-data"))


def espeak_binary() -> str | None:
    """Return the espeak-ng command-line program to run for speech."""
    base = bundled_dir()
    if base is not None:
        return str(base / BINARY_NAME)
    return shutil.which("espeak-ng") or shutil.which("espeak")


def espeak_data_args() -> list[str]:
    base = bundled_dir()
    return ["--path", str(base / "espeak-ng-data")] if base is not None else []


def espeak_env() -> dict[str, str] | None:
    """Environment for the espeak-ng program so it finds the bundled library."""
    base = bundled_dir()
    if base is None:
        return None
    env = dict(os.environ)
    for variable in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
        env[variable] = os.pathsep.join(
            part for part in (str(base), env.get(variable, "")) if part
        )
    env["PATH"] = os.pathsep.join(part for part in (str(base), env.get("PATH", "")) if part)
    return env

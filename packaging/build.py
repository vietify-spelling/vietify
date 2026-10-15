"""Build the Vietify desktop app with PyInstaller.

Usage (from the project root, with the build extra installed):
    python -m pip install -e ".[gui,build]"
    python packaging/build.py

Finds espeak-ng on this machine, bundles it, then writes:
    dist/Vietify/            Linux and Windows: folder with the app
    dist/Vietify.app         macOS: the app bundle
    dist/Vietify-<os>.zip    the same app, zipped for distribution

Override the espeak-ng files with environment variables if needed:
    ESPEAK_NG_LIB   path to libespeak-ng (.so.1 / .dylib / .dll)
    ESPEAK_NG_BIN   path to the espeak-ng program
    ESPEAK_NG_DATA  path to the espeak-ng-data folder
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
STAGE = BUILD / "espeak"


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def find_espeak() -> tuple[Path, Path, Path]:
    """Return (library, program, data) for espeak-ng on this machine."""
    env = {k: os.environ.get(k) for k in ("ESPEAK_NG_LIB", "ESPEAK_NG_BIN", "ESPEAK_NG_DATA")}
    if all(env.values()):
        return Path(env["ESPEAK_NG_LIB"]), Path(env["ESPEAK_NG_BIN"]), Path(env["ESPEAK_NG_DATA"])

    if sys.platform == "win32":
        root = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "eSpeak NG"
        lib, binary, data = root / "libespeak-ng.dll", root / "espeak-ng.exe", root / "espeak-ng-data"
    elif sys.platform == "darwin":
        prefix = next((p for p in ("/opt/homebrew", "/usr/local") if Path(p, "lib/libespeak-ng.dylib").exists()), None)
        if prefix is None:
            fail("espeak-ng not found; install it with `brew install espeak-ng`")
        lib = Path(prefix, "lib/libespeak-ng.dylib")
        binary = Path(prefix, "bin/espeak-ng")
        data = Path(prefix, "share/espeak-ng-data")
    else:
        libs = sorted(glob.glob("/usr/lib/*/libespeak-ng.so.1") + glob.glob("/usr/lib/libespeak-ng.so.1"))
        datas = sorted(glob.glob("/usr/lib/*/espeak-ng-data") + glob.glob("/usr/share/espeak-ng-data"))
        lib = Path(libs[0]) if libs else Path("missing")
        binary = Path(shutil.which("espeak-ng") or "missing")
        data = Path(datas[0]) if datas else Path("missing")

    for path in (lib, binary, data):
        if not path.exists():
            fail(f"espeak-ng file not found: {path} (set ESPEAK_NG_* environment variables)")
    return lib.resolve(), binary.resolve(), data.resolve()


# espeak-ng dictionaries kept in the app: en (en-gb/en-us/en-au), fr, de, ru,
# cmn (Mandarin, "ch") and ja. Others are removed to shrink the bundle.
KEEP_DICTS = {"en", "fr", "de", "ru", "cmn", "ja"}


def prune_espeak_data(data: Path) -> None:
    """Remove dictionaries and voices for languages the app does not use."""
    for dictionary in data.glob("*_dict"):
        if dictionary.name[: -len("_dict")] not in KEEP_DICTS:
            dictionary.unlink()
    shutil.rmtree(data / "mbrola_ph", ignore_errors=True)


def stage_espeak() -> None:
    """Copy espeak-ng into build/espeak under the names the app expects."""
    from vietify.espeak_runtime import BINARY_NAME, LIBRARY_NAME

    lib, binary, data = find_espeak()
    shutil.rmtree(STAGE, ignore_errors=True)
    STAGE.mkdir(parents=True)
    shutil.copy2(lib, STAGE / LIBRARY_NAME)
    shutil.copy2(binary, STAGE / BINARY_NAME)
    shutil.copytree(data, STAGE / "espeak-ng-data")
    prune_espeak_data(STAGE / "espeak-ng-data")


def pyinstaller_command() -> list[str]:
    sep = os.pathsep
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--windowed", "--onedir",
        "--name", "Vietify",
        "--paths", str(ROOT / "src"),
        "--collect-all", "tkinterdnd2",
        "--collect-submodules", "vietify",
        "--hidden-import", "PIL._tkinter_finder",
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(BUILD / "pyinstaller"),
        "--specpath", str(BUILD),
    ]
    # Shared libraries and the program go into <bundle>/espeak, so PyInstaller
    # also bundles their dependencies.
    for name in ("libespeak-ng.so.1", "libespeak-ng.dylib", "libespeak-ng.dll", "espeak-ng", "espeak-ng.exe"):
        if (STAGE / name).exists():
            command += ["--add-binary", f"{STAGE / name}{sep}espeak"]
    command += ["--add-data", f"{STAGE / 'espeak-ng-data'}{sep}espeak/espeak-ng-data"]
    if sys.platform == "darwin":
        command += ["--osx-bundle-identifier", "com.vietify.app"]
    command.append(str(ROOT / "packaging" / "launch_gui.py"))
    return command


def main() -> int:
    stage_espeak()
    subprocess.run(pyinstaller_command(), cwd=ROOT, check=True)

    app_name = "Vietify.app" if sys.platform == "darwin" else "Vietify"
    app_dir = ROOT / "dist" / app_name
    platform = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")
    archive = shutil.make_archive(str(ROOT / "dist" / f"Vietify-{platform}"), "zip", ROOT / "dist", app_name)
    print(f"\nBuilt: {app_dir}\nArchive: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

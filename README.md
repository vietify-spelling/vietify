# Vietify

**Give foreign pronunciation a Vietnamese-style spelling.**

Vietify converts text or IPA (International Phonetic Alphabet) into Vietnamese-inspired phonetic spelling.

It can phonemize:

* English
* French
* German
* Mandarin Chinese
* Japanese
* Russian
* Potentially other languages supported by eSpeak NG

Vietify does **not** translate meaning. It is designed as a pronunciation aid for Vietnamese speakers learning foreign-language pronunciation.

This project is a modification and extension of [ipa-to-vie](https://github.com/vuadu/ipa-to-vie).

## Quick Start

### Requirements

* Python 3
* [eSpeak NG](https://github.com/espeak-ng/espeak-ng), used by the phonemizer

On Debian or Ubuntu:

```sh
sudo apt install espeak-ng
```

Install Python dependencies:

```sh
python -m pip install -e .
```

Run Vietify from the project directory:

```sh
vietify "Hello world"
```

The default input language is English, and the default conversion mode is `weak`.

For multi-word input, wrap the text in quotes so it is passed as a single argument:

```sh
vietify --language fr --mode weak "Bonjour tout le monde"
```

Example output:

```text
bông-ʒuʁ tul-môngd
```

### Convert a text file

Use `--input-file` and `--output-file` to process a UTF-8 text file in one run.
Each non-empty input line is converted once and written with its original text,
IPA, strong spelling, and weak spelling:

```sh
vietify --language de \
  --input-file input.txt \
  --output-file result.txt
```

The output directory is created automatically. You can also run the test corpus
processor with `python test/test.py`. It converts every `.txt` file under
`test/testcases/<language>/` and writes corresponding files under
`test/generatedResult/<language>/`.

The corpus has no expected output. Review the generated files by eye. Each
language directory contains:

* `allPhonemes_*.txt`: sentences covering the phoneme inventory.
* `phonemeCombinations_*.txt`: longer text covering phoneme combinations, one
  sentence per line.

Warnings go to stderr and do not stop the run. `test/test.py` prints them as
`[WARN]` lines. Two cases trigger them:

* espeak output contains characters it cannot encode (`?` or U+FFFD). These
  characters are dropped from the word, so the rest of the word is still
  converted.
* the input is mixed-language and espeak adds `(xx)` markers. The token is
  left unconverted.

## Languages

Select the input language with `-l` or `--language`:

| Option    | Language                      |
| --------- | ----------------------------- |
| `en-us`   | English (US, default)         |
| `en-gb`   | English (British)             |
| `en-au`   | English (Australian)          |
| `fr`      | French                        |
| `de`      | German                        |
| `ch`      | Mandarin Chinese pinyin       |
| `ja`      | Japanese                      |
| `ru`      | Russian                       |
| `ipa`     | Input is already IPA          |

For example:

```sh
vietify -l fr "Bonjour"
```

For Mandarin, provide pinyin rather than Chinese characters. Pinyin tone
marks and trailing tone numbers (1-5, with 0 also accepted for neutral tone)
are supported. Separate syllables with spaces:

```sh
vietify -l ch -m weak "nǐ hǎo"
vietify -l ch -m strong "ni3 hao3"
```

If you already have an IPA transcription, use `ipa` to skip text phonemization:

```sh
vietify -l ipa "ˈwɛt"
```

## Conversion Modes

Select a mode with `-m` or `--mode`:

| Mode     | Description                                                                                                                                                                           |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `weak`   | Default. Preserves foreign phonemes more faithfully while applying Vietnamese-style spelling rules.                                                                                   |
| `strong` | Applies stronger Vietnamese adaptation. Phonemes that do not exist in Vietnamese are replaced with approximate Vietnamese sounds, with configured vowel insertion for some syllables. |
| `ipa`    | Phonemizes text and outputs normalized IPA without converting it into Vietnamese-style spelling.                                                                                      |

### Examples

```sh
vietify --mode ipa "Japan is Turning Footsteps Into Electricity"

vietify --mode weak "Japan is Turning Footsteps Into Electricity"

vietify --mode strong "Japan is Turning Footsteps Into Electricity"
```

Output:

```text
dʒəpan ɪz tənɪŋ fʊtstɛps ɪntʊ ɪlɛktɹɪsɪti

dʒơ-pan iz tơ-ning phut-x-tep-x in-tu i-lech-tri-xi-ty

giơ-pan it tơ-ning phut-xơ-tep-xơ in-tu i-lech-tri-xi-ty
```

The `ipa` mode is useful for inspecting the pronunciation produced by the phonemizer before Vietnamese conversion.

Alternatively, use `--language ipa` when the input is already IPA.

## Python API

The `ipa_to_vie()` function converts IPA into a list of result dictionaries.

Each result contains the original IPA, its parsed representation, and its Vietnamese-style spelling:

```python
from vietify import ipa_to_vie

results = ipa_to_vie("ˈwɛt", mode="weak")

print(results[0]["vie"])
```

For pronunciation from ordinary text, use the CLI. Text phonemization is handled by the `phonemizer` package using eSpeak NG.

## GUI

A minimal Tkinter window covers the same options as the CLI:

```sh
python -m pip install -e ".[gui]"
vietify-gui
```

* Paste text into the box, pick a language and an output mode, then press
  Ctrl+Enter or **Convert**. The default mode shows IPA, strong and weak
  results below the input.
* Drop a `.txt` file onto the window or use **Browse…**. File input uses the
  batch path, so it always writes IPA, strong and weak, as `--input-file`
  does. **Output file…** opens a save dialog.

Drag-and-drop needs `tkinterdnd2`, installed by the `gui` extra. Without it,
use **Browse…**.

* The speaker button next to the input box reads the pasted text aloud in the
  selected language, using espeak-ng. Press it again to stop. It is not
  available for the `ipa` language, since espeak cannot read IPA.

## Desktop app

You can build a standalone desktop app that needs no Python or espeak-ng
install. It bundles espeak-ng, tkinterdnd2 and the GUI. Build it on the OS you
want to ship for: PyInstaller does not cross-compile.

Common steps (all systems):

1. Install Python 3.10 or newer and espeak-ng (per-system steps below).
2. From the project folder, install the GUI and build tools:
   `python -m pip install -e ".[gui,build]"`
3. Build: `python packaging/build.py`
4. The app is in `dist/` and a zip is written next to it.

**Windows**

1. Install [eSpeak NG](https://github.com/espeak-ng/espeak-ng/releases) with
   the Windows installer (default location `C:\Program Files\eSpeak NG`).
2. In PowerShell from the project folder:
   `py -m pip install -e ".[gui,build]"` then `py packaging\build.py`.
3. Run `dist\Vietify\Vietify.exe`. The first run may show a SmartScreen
   warning because the app is unsigned: choose *More info → Run anyway*.

**Linux (Debian/Ubuntu)**

1. `sudo apt install espeak-ng python3-tk python3-venv`
2. `python3 -m venv .venv && .venv/bin/python -m pip install -e ".[gui,build]"`
3. `.venv/bin/python packaging/build.py`
4. Run `dist/Vietify/Vietify`. Copy the `dist/Vietify` folder to share it.

**macOS**

1. `brew install espeak-ng python-tk`
2. `python3 -m pip install -e ".[gui,build]"` then `python3 packaging/build.py`
3. Open `dist/Vietify.app`. The app is unsigned, so the first launch needs
   *right-click → Open*, or `xattr -dr com.apple.quarantine dist/Vietify.app`.

Override the espeak-ng files with `ESPEAK_NG_LIB`, `ESPEAK_NG_BIN` and
`ESPEAK_NG_DATA` if they are installed in a non-standard place.

To check a build, run `dist/Vietify/Vietify --self-test` (or
`dist/Vietify.app/Contents/MacOS/Vietify --self-test`). It converts a sample,
runs the bundled espeak-ng, and prints `SELF-TEST OK`.

Notes:
- Only Linux was built and tested. Windows and macOS need a build on that
  system; the same script covers them, but it has not been run there.
- The app folder is about 120 MB (mostly Python, numpy and Tcl/Tk); the espeak-ng data is trimmed to the languages Vietify uses.
- Distributing the app means distributing espeak-ng, so the GPL terms in
  [License](#license) apply.

## License

Vietify is free software under the [GNU GPL v3 or later](LICENSE). It is
based on [ipa-to-vie](https://github.com/vuadu/ipa-to-vie) (MIT) and uses
espeak-ng (GPL-3.0). See [THIRD_PARTY.md](THIRD_PARTY.md) for all components
and the MIT notice that must be kept.

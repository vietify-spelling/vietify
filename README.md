# Vietify

**Give foreign pronunciation a Vietnamese-style spelling.**

Vietify converts text or IPA (International Phonetic Alphabet) into Vietnamese-inspired phonetic spelling.

It can phonemize:

* English
* French
* German
* Mandarin Chinese
* Japanese
* Korean
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
python -m pip install -r requirements.txt
```

Run Vietify from the project directory:

```sh
python main.py "Hello world"
```

The default input language is English, and the default conversion mode is `weak`.

For multi-word input, wrap the text in quotes so it is passed as a single argument:

```sh
python main.py --language fr --mode weak "Bonjour tout le monde"
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
python main.py --language de \
  --input-file input.txt \
  --output-file result.txt
```

The output directory is created automatically. You can also run the test corpus
processor with `python test/test.py` when your corpus is organized under
`test/testcases/<language>/`; it writes corresponding files under
`test/generatedResult/`.

## Languages

Select the input language with `-l` or `--language`:

| Option | Language                      |
| ------ | ----------------------------- |
| `en`   | English (US phonemizer voice) |
| `fr`   | French                        |
| `de`   | German                        |
| `ch`   | Mandarin Chinese pinyin       |
| `ja`   | Japanese                      |
| `ko`   | Korean                        |
| `ru`   | Russian                       |
| `ipa`  | Input is already IPA          |

For example:

```sh
python main.py -l fr "Bonjour"
```

For Mandarin, provide pinyin rather than Chinese characters. Pinyin tone
marks and trailing tone numbers (1-5, with 0 also accepted for neutral tone)
are supported. Separate syllables with spaces:

```sh
python main.py -l ch -m weak "nǐ hǎo"
python main.py -l ch -m strong "ni3 hao3"
```

If you already have an IPA transcription, use `ipa` to skip text phonemization:

```sh
python main.py -l ipa "ˈwɛt"
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
python main.py --mode ipa "Japan is Turning Footsteps Into Electricity"

python main.py --mode weak "Japan is Turning Footsteps Into Electricity"

python main.py --mode strong "Japan is Turning Footsteps Into Electricity"
```

Output:

```text
dʒəpan ɪz tənɪŋ fʊtstɛps ɪntʊ ɪlɛktɹɪsɪti

dʒơ-pan i-z tơ-ning phut-x-tep-x in-tu i-lech-tri-xi-ty

dờ-pờ ì-dờ thờ-nình phụt-xờ-thẹp-xờ ìn-thù ì-lệch-trì-xì-thỳ
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

## License

This project is released into the public domain. See [LICENSE](LICENSE).

Based on @vuadu/ipa-to-vie by Rezza Inc.
Original: https://github.com/vuadu/ipa-to-vie
Licensed under MIT.

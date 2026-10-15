# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment and commands

- Python env lives in `.venv/` (Python 3.12). Use `.venv/bin/python`. Deps: `requirements.txt` (phonemizer needs eSpeak NG installed on the system, e.g. `sudo apt install espeak-ng`).
- No build step, no linter/formatter config.
- Package layout: `src/vietify/` (installed editable). Install with `.venv/bin/python -m pip install -e .`. Tests import `vietify.*` and need that install:
  - All Hepburn tests: `.venv/bin/python -m unittest test.test_hepburn`
  - Single test: `.venv/bin/python -m unittest test.test_hepburn.HepburnConversionTests.test_nasal_assimilates_across_whitespace`
- CLI: `.venv/bin/vietify -l fr "Bonjour"` or `.venv/bin/python -m vietify -l fr "Bonjour"` (flags: `-l/--language`, `-m/--mode weak|strong|ipa`, `--input-file` + `--output-file` for batch).
- `test/test.py` is a corpus runner, not an assertion test. It runs `python -m vietify` over every `test/testcases/<lang>/*.txt` and writes `test/generatedResult/`. Compare outputs by eye/diff; it does not fail on wrong output.

## Current state

- `parser.py` grammar loads and nasal vowels (including nasal + coda) parse. Unit tests: `test_hepburn` 8/8 pass.
- Warnings (stderr, `logger.warning`) for espeak undecodable output (`?`, U+FFFD) and language-switch tokens `(…)`. `test/test.py` prints them as `[WARN]`.
- Known open issues and suggested fixes are in `REPORT.md`.

## Architecture

Text-to-spelling pipeline, all orchestrated in `src/vietify/main.py`:

1. **Phonemize** (`main.py:_text_to_pronunciation`): `phonemizer` + eSpeak NG for languages in `PHONEMIZER_LANGUAGES`. Skipped for `ch` (pinyin input), `ja` (Hepburn input) and `ipa` (input already IPA).
2. **Normalize** (`main.py:normalize_phonemized_ipa`): eSpeak quirks to canonical IPA (e.g. `ɚ`→`əɹ`, Russian palatalized consonants → `Cj`). Skipped for `ch`/`ja`. French keeps nasalization tilde.
3. **Convert per word** (`main.py:_convert_pronunciation`): splits on whitespace, keeps leading/trailing punctuation, then dispatches:
   - IPA langs → `converter.ipa_to_vie` → `parser.parse` (parsimonious grammar → syllable dicts `{stress, initial, nucleus, ending}`) → rule table mapping (`IPAruleWeak`/`IPAruleStrong`) → hyphenated Vietnamese syllables.
   - `ch` → `converter.pinyin_to_vie` (`pinyinParser.py` + `pinyinRuleWeak`/`pinyinRuleStrong`). Tone numbers/marks become Vietnamese tone diacritics via `add_tonal_mark_to_vowel`.
   - `ja` → `converter.hepburn_to_vie` (`hepburnParser.py` + `hepburnRuleStrong.py`). Whole-string, not per-word, because nasal `n` assimilates across word boundaries (`nasal_realization`). Ignores weak/strong distinction; always uses the strong table.
   - `fr` → post-pass `_apply_french_liaison` appends ` →` after words ending in liaison consonants before a vowel-initial word.
4. Output is joined with spaces (Japanese returns the whole string directly).

Rule tables share a shape (`LETTER_MAPPING`, `SYLLABLE_ENDING_MAPPING`, `NULL_MAPPING`; see `ConversionRules` in `converter.py`). Weak vs strong differs in:
- **weak**: keep foreign phonemes; strip `NULL_MAPPING` (`_`) placeholders.
- **strong**: replace unsupported phonemes with Vietnamese approximations; for syllables with no vowel, insert an epenthetic vowel (default `ơ`, configurable via `options["vowelEpenthesis"]`).

Post-processing in `converter.py` applies Vietnamese spelling rules on the joined syllable: `wi→uy`/`ge→ghe`-style substitutions, final `-i→-y` after consonants, `c/k` alternation (`vie_consonant_rule`), final `c→ch` after `e/i`. Tone marks use `COMBINE_*` constants and are placed on the Vietnamese nucleus vowel.

Batch mode (`main.py:process_text_file`): each non-empty line yields four lines (input, IPA, strong, weak) plus a blank line. Errors are collected per line, blank/placeholder output is written, and the run then raises with the list. Output is still written.

## Gotchas

- `-l en` appears in README's language table but is not a valid choice. Valid English values are `en-us` (default), `en-gb`, `en-au`.
- `-l ko` is accepted by argparse but commented out of `PHONEMIZER_LANGUAGES`. Text input crashes with `KeyError` (not caught by `main()`'s handler).
- Mandarin takes pinyin, not Hanzi. Hepburn takes romanized Japanese, not kana.
- `hepburnParser` rejects `j` as a y-glide (`sja`, `zja` etc. raise `ValueError`). That is tested behavior, not a bug.
- `ipa_to_vie` splits on `", "` (comma+space), not whitespace.
- `test/testcases/` and `test/generatedResult/` are partly gitignored; add test corpora under `test/testcases/<lang>/`.

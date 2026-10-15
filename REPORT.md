# Vietify: potential problems and improvements

Scope: code and generated output in `test/generatedResult/`.
Items marked **verified** were reproduced by running the CLI or converter.

## 1. Output quality

### 1.1 Pinyin consonant mapping is questionable (read from code)

`pinyinRuleWeak.py` `LETTER_MAPPING` maps `j → tr`, `q → trh`, `zh → ch`,
`ch → chh`, `z → ts`, `c → tsh`. Pinyin `j/q/x` are alveolo-palatal, while
`zh/ch/sh` are retroflex. Mapping `j` to `tr` (retroflex in Vietnamese) and
`zh` to `ch` may swap the two series. Verify against a listening reference
before changing. `chh`, `trh`, `tsh` are not Vietnamese spellings either.


## 2. Japanese / Hepburn

- **weak and strong are identical.** `hepburn_to_vie` always uses
  `hepburnRuleStrong`. The existing weak test (`san mai.` → `sam mai.`)
  asserts nasal assimilation in weak mode, so the current design treats the
  two modes as the same. Decide whether weak should differ (e.g. keep
  `hepburnRuleWeak` with raw spelling) and update the tests to match.
- The `ja` path skips phonemization and normalization, so the espeak
  warnings do not apply. Hepburn input with `?` or `(` is not checked.
- Doubled consonants (sokuon, e.g. `katte`) are not parsed: `hepburn_to_vie`
  raises `could not parse Hepburn input`. The Japanese corpus avoids them.


## 4. README

- The strong example in README (`dờ-pờ ì-dờ thờ-nình …`) no longer matches
  current output (verified: current strong gives `ghiơ-pan it tơ-ning …`).
  Regenerate the examples from the CLI.

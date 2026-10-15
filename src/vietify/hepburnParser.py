import unicodedata


VOWELS = frozenset("aāeēiīoōuū")
_DIPHTHONGS = frozenset({"ai", "au", "ei", "oi", "ou", "ui"})
_ONSETS = (
    "ch", "sh", "ts",
    "by", "dy", "gy", "hy", "jy", "ky", "my", "ny", "py", "ry", "sy", "ty", "zy",
    "b", "d", "f", "g", "h", "j", "k", "m", "n", "p", "r", "s", "t", "w", "y", "z",
)


class HepburnParseError(ValueError):
    """Raised when a romanized Japanese word is not valid Hepburn input."""


def _append_moraic_nasal(syllables: list[dict[str, str | None]]) -> None:
    if syllables and syllables[-1]["nucleus"] and not syllables[-1]["ending"]:
        syllables[-1]["ending"] = "n"
        return

    syllables.append({
        "initial": None,
        "nucleus": None,
        "ending": "n",
        "nasal_realization": None,
    })


def parse(text: str) -> list[dict[str, str | None]]:
    """Parse one Hepburn word into onset, nucleus, and moraic-nasal fields."""
    word = unicodedata.normalize("NFC", text).lower().replace("’", "'")
    if not word:
        raise HepburnParseError("Hepburn input cannot be empty")

    syllables: list[dict[str, str | None]] = []
    index = 0

    while index < len(word):
        if word[index] == "n" and (
            index + 1 == len(word)
            or word[index + 1] == "'"
            or word[index + 1] not in VOWELS | {"y"}
        ):
            _append_moraic_nasal(syllables)
            index += 1
            if index < len(word) and word[index] == "'":
                index += 1
            continue

        onset = next(
            (candidate for candidate in _ONSETS if word.startswith(candidate, index)),
            "",
        )
        if onset:
            index += len(onset)
        elif word[index] in VOWELS:
            onset = ""
        else:
            raise HepburnParseError(
                f"invalid Hepburn sequence at position {index}: {word[index:]!r}"
            )

        if index >= len(word) or word[index] not in VOWELS:
            raise HepburnParseError(
                f"expected a vowel after {onset or 'word start'} in {word!r}"
            )

        nucleus = word[index]
        if (
            index + 1 < len(word)
            and nucleus + word[index + 1] in _DIPHTHONGS
        ):
            nucleus += word[index + 1]
            index += 1
        index += 1

        syllables.append({
            "initial": onset or None,
            "nucleus": nucleus,
            "ending": None,
            "nasal_realization": None,
        })

    return syllables

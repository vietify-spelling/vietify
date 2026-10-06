import logging
import re
import unicodedata
from typing import Literal, Protocol

from parsimonious.exceptions import ParseError

from . import (
    IPAruleStrong,
    IPAruleWeak,
    pinyinRuleStrong,
    pinyinRuleWeak,
)

from .parser import parse
from .pinyinParser import parse as parse_pinyin

logger = logging.getLogger(__name__)

RuleMode = Literal["weak", "strong"]
COMBINE_ACUTE = "\u0301"      # sắc: á
COMBINE_GRAVE = "\u0300"      # huyền: à
COMBINE_HOOK_ABOVE = "\u0309" # hỏi: ả
COMBINE_TILDE = "\u0303"      # ngã: ã
COMBINE_DOT = "\u0323"        # nặng: ạ
COMBINE_NONE = ""              # ngang: a


COMBINE_MACRON = "\u0304"  # 1st: mā

class ConversionRules(Protocol):
    """Rule table required by syllable-to-Vie conversion."""

    SYLLABLE_ENDING_MAPPING: dict[str, str]
    LETTER_MAPPING: dict[str, str]
    NULL_MAPPING: Literal["_"]


_RULES: dict[RuleMode, ConversionRules] = {
    "weak": IPAruleWeak,
    "strong": IPAruleStrong,
}

_PINYIN_RULES: dict[RuleMode, ConversionRules] = {
    "weak": pinyinRuleWeak,
    "strong": pinyinRuleStrong,
}


def _rules_for_mode(
    mode: RuleMode,
    language: str | None = None,
) -> ConversionRules:
    """Return rule table for mode, raising ValueError for unsupported modes."""
    rule_tables = _PINYIN_RULES if language == "ch" else _RULES
    try:
        return rule_tables[mode]
    except KeyError:
        raise ValueError(
            f"mode must be 'weak' or 'strong', got {mode!r}"
        ) from None


def normalize_nfc(value: str) -> str:
    """Normalize Unicode to NFC so composed Vietnamese characters compare consistently."""
    return unicodedata.normalize("NFC", value)


def normalize_nfd(value: str) -> str:
    """Normalize Unicode to NFD for inspecting a base character."""
    return unicodedata.normalize("NFD", value)


def vie_consonant_rule(consonant: str, vowel: str) -> str:
    """Resolve c/k alternation required by following vowel."""

    # k/c + u + vowel -> qu + vowel
    if (
        vowel
        and consonant in {"k", "c"}
        and normalize_nfd(vowel[0])[0] == "u"
        and len(vowel) > 1
        and normalize_nfd(vowel[1])[0] in {
            "a", "e", "ê", "i", "o", "u", "œ", "ø", "ä", "ö", "ü", 
        }
    ):
        return "qu" + vowel[1:]

    if (
        vowel
        and consonant == "k"
        and normalize_nfd(vowel[0])[0] in {"a", "o", "u", "ä", "ü",}
    ):
        return "c" + vowel

    if (
        vowel
        and consonant == "c"
        and normalize_nfd(vowel[0])[0] in {"e", "ê", "i", "œ", "ø"}
    ):
        return "k" + vowel

    return consonant + vowel

_VIE_SYLLABLE_REPLACEMENTS = {
    "wi": "uy",
    "wa": "oa",
    "wâ": "uâ",
    "we": "oe",
    "wơ": "uơ",
    "ge": "ghe",
    "gi": "ghi",
    "gê": "ghê",
    "qui": "quy",
}

_VIE_SYLLABLE_PATTERN = re.compile(
    r"wi|wa|wâ|we|wơ|ge|gi(?!a)|gê|qui"
    # r"wi|wa|wâ|we|wơ|ge|gê|qui"
)

_ENDING_REPLACEMENTS = {
    "ki": "ky",
    "li": "ly",
    "mi": "my",
    "si": "sy",
    "ti": "ty",
    "hi": "hy",
}

_ENDING_PATTERN = re.compile(
    r"ki$|li$|mi$|si$|ti$|hi$"
)


def _replace_vie_syllable_patterns(vie: str) -> str:
    """Apply spelling substitutions that operate on complete Vie syllables."""
    return _VIE_SYLLABLE_PATTERN.sub(
        lambda match: _VIE_SYLLABLE_REPLACEMENTS[match.group(0)],
        vie,
    )


def _apply_vowel_epenthesis(
    vie: str,
    options: dict,
) -> str:
    """Insert configured vowel into syllables whose vowel is missing."""
    vowel_epenthesis = options.get("vowelEpenthesis", {})

    def replace_epenthesis(match: re.Match) -> str:
        consonant = match.group(0)[0]
        replacement = vowel_epenthesis.get(
            "replacement",
            "ơ",
        )
        return vie_consonant_rule(
            consonant,
            replacement,
        )

    return re.sub(
        r"._",
        replace_epenthesis,
        vie,
    )


def _apply_ending_replacements(vie: str) -> str:
    """Apply final -i -> -y spelling substitutions."""
    return _ENDING_PATTERN.sub(
        lambda match: _ENDING_REPLACEMENTS[match.group(0)],
        vie,
    )

def _apply_initial_consonant_rule(vie: str) -> str:
    """Apply c/k spelling rule to initial consonant."""

    if len(vie) < 2 or vie[0] not in {"k", "c"}:
        return vie

    return vie_consonant_rule(vie[0], vie[1:])

def _apply_final_k_rule(vie: str) -> str:
    """Apply Vietnamese c/ch spelling rule to final /k/."""

    if not vie.endswith("c"):
        return vie

    if len(vie) < 2:
        return vie

    preceding = normalize_nfd(vie[-2])[0]

    if preceding in {"e", "ê", "i"}:
        return vie[:-1] + "ch"

    return vie

def _should_skip_vowel_epenthesis(
    options: dict,
    is_last_syllable: bool,
) -> bool:
    """Return whether vowel epenthesis should be skipped for current syllable."""
    vowel_epenthesis = options.get("vowelEpenthesis", {})

    return (
        vowel_epenthesis.get("skipAll")
        or (
            vowel_epenthesis.get("skipLast")
            and is_last_syllable
        )
    )


def _build_vie_syllable(
    syllable: dict,
    rules: ConversionRules,
    language: str | None = None,
    has_following_consonant: bool = False,
) -> tuple[str, bool]:
    """Map parser AST syllable components into an intermediate Vie syllable.

    Returns:
        (syllable, is_null_vowel)
    """
    head = syllable.get("initial") or ""
    nucleus = syllable.get("nucleus") or ""
    ending = syllable.get("ending") or ""

    tail = nucleus + ending
    syllable_ending_mapping = rules.SYLLABLE_ENDING_MAPPING
    if language == "de":
        syllable_ending_mapping = {
            **syllable_ending_mapping,
            **IPAruleWeak.GERMAN_R_VOCALIZATION,
        }
        if not has_following_consonant:
            syllable_ending_mapping.update(
                IPAruleWeak.GERMAN_R_VOCALIZATION_WITHOUT_CODA,
            )

    is_null_ending = tail not in syllable_ending_mapping

    vie = (
        rules.LETTER_MAPPING.get(head, "")
        + syllable_ending_mapping.get(
            tail,
            rules.NULL_MAPPING,
        )
    )

    return _replace_vie_syllable_patterns(vie), is_null_ending


def syllable_to_vie(
    syllable: dict,
    options: dict | None = None,
    is_last_syllable: bool = False,
    *,
    mode: RuleMode,
    has_following_consonant: bool = False,
) -> str:
    """Convert one parser AST syllable into Vie spelling.

    Strong mode preserves additional information such as stress and can
    insert epenthetic vowels. Weak mode removes null-vowel placeholders.
    """
    options = options or {}
    rules = _rules_for_mode(mode, options.get("language"))

    vie_syllable, is_null_vowel = _build_vie_syllable(
        syllable,
        rules,
        language=options.get("language"),
        has_following_consonant=has_following_consonant,
    )

    if is_null_vowel:
        if mode == "strong":
            if _should_skip_vowel_epenthesis(
                options,
                is_last_syllable,
            ):
                return ""

            vie_syllable = _apply_vowel_epenthesis(
                vie_syllable,
                options,
            )
        else:
            vie_syllable = vie_syllable.replace(
                rules.NULL_MAPPING,
                "",
            )
    else:
        vie_syllable = _apply_ending_replacements(
            vie_syllable,
        )
        vie_syllable = _apply_initial_consonant_rule(
            vie_syllable,
        )

        vie_syllable = _apply_final_k_rule(
            vie_syllable,
        )

    # if mode == "strong":
        # vie_syllable = add_tonal_mark(
        #     vie_syllable,
        #     syllable.get("stress"),
        # )

    if options.get("uppercaseStress") and syllable.get("stress"):
        return vie_syllable.upper()

    return vie_syllable


def _clean_ipa_item(item: str) -> str:
    """Normalize IPA variants that parser does not consume directly."""
    return (
        item
        .replace("ɝˈ", "əˈɹ")
        .replace("ɝ", "əɹ")
    )


def _normalize_stress(ast: list[dict]) -> None:
    """Remove secondary stress when every vowel already has stress."""
    stress_count = sum(
        1 for syllable in ast
        if syllable.get("stress")
    )

    vowel_count = sum(
        1 for syllable in ast
        if syllable.get("nucleus")
    )

    if stress_count != vowel_count:
        return

    secondary = next(
        (
            syllable
            for syllable in ast
            if syllable.get("stress") == 2
        ),
        None,
    )

    if secondary:
        secondary["stress"] = None


def _move_stress_from_empty_syllables(
    ast: list[dict],
) -> None:
    """Move stress from syllable without nucleus onto following syllable."""
    for idx, syllable in enumerate(ast):
        if (
            syllable.get("stress")
            and not syllable.get("nucleus")
            and idx + 1 < len(ast)
        ):
            ast[idx + 1]["stress"] = syllable["stress"]
            syllable["stress"] = None


def _convert_ast_to_vie(
    ast: list[dict],
    options: dict,
    mode: RuleMode,
) -> str:
    """Convert parsed IPA AST into hyphen-separated Vie syllables."""
    last_syllable_idx = len(ast) - 1
    vie_parts = []

    for idx, syllable in enumerate(ast):
        vie_syl = syllable_to_vie(
            syllable=syllable,
            options=options,
            is_last_syllable=(
                idx == last_syllable_idx
            ),
            mode=mode,
            has_following_consonant=(
                idx + 1 < len(ast)
                and bool(ast[idx + 1].get("initial"))
                and not ast[idx + 1].get("nucleus")
            ),
        )

        if idx != 0 and vie_syl:
            vie_parts.append("-")

        vie_parts.append(vie_syl)

    return "".join(vie_parts)


def _convert_ipa_item(
    item: str,
    options: dict,
    mode: RuleMode,
) -> dict:
    """Parse and convert one IPA item.

    Kept separate from `ipa_to_vie` so failures can be traced to one
    IPA item without losing surrounding input context.
    """
    cleaned = _clean_ipa_item(item)

    logger.debug(
        "IPA conversion start: item=%r cleaned=%r mode=%s options=%r",
        item,
        cleaned,
        mode,
        options,
    )

    ast = parse(cleaned)

    logger.debug(
        "IPA parsed: item=%r ast=%r",
        item,
        ast,
    )

    _normalize_stress(ast)
    _move_stress_from_empty_syllables(ast)

    vie = _convert_ast_to_vie(
        ast,
        options,
        mode,
    )

    logger.debug(
        "IPA conversion complete: item=%r vie=%r ast=%r",
        item,
        vie,
        ast,
    )

    return {
        "ipa": item,
        "ast": ast,
        "vie": vie,
    }

_LIAISON_CONSONANTS = {
    "z", "x",  # z liaison
    "t", "d",       # t liaison
    "n",            # n liaison
    "ph",            # v liaison
    # "p", "r", 
}
_VOWELS = set("aeêiouœøäöü")

def _apply_french_liaison(results: list[dict]) -> list[dict]:
    """Mark liaison between adjacent converted words."""

    for current, following in zip(results, results[1:]):
        current_vie = current["vie"]
        following_vie = following["vie"]

        if (
            current_vie
            and following_vie
            # and current_vie[-1].lower() in _LIAISON_CONSONANTS
            and any(current_vie.lower().endswith(c) for c in _LIAISON_CONSONANTS)
            and following_vie[0].lower() in _VOWELS
        ):
            current["vie"] = current_vie + " →"

    return results

def ipa_to_vie(
    ipa: str,
    options: dict | None = None,
    *,
    mode: RuleMode,
) -> list[dict]:
    """Convert comma-separated IPA items into Vie representations.

    Each result contains original IPA, parsed AST, and converted Vie text.
    Exceptions retain their original traceback while logging enough context
    to identify failing input and conversion mode.
    """
    options = options or {}
    _rules_for_mode(mode)

    results = []

    logger.debug(
        "IPA batch conversion start: ipa=%r mode=%s options=%r",
        ipa,
        mode,
        options,
    )

    for index, item in enumerate(ipa.split(", ")):
        try:
            results.append(
                _convert_ipa_item(
                    item,
                    options,
                    mode,
                )
            )
        except Exception:
            logger.exception(
                "IPA conversion failed: "
                "index=%d item=%r cleaned=%r mode=%s options=%r",
                index,
                item,
                _clean_ipa_item(item),
                mode,
                options,
            )
            raise

    if options.get("language") == "fr":
        results = _apply_french_liaison(results)


    logger.debug(
        "IPA batch conversion complete: count=%d mode=%s",
        len(results),
        mode,
    )

    return results

def add_tonal_mark_to_vowel(vie: str, tonal_mark: str) -> str:
    """Attach tonal mark to the preferred Vietnamese nucleus vowel."""

    # Multi-vowel nuclei where the tone belongs on the second vowel.
    for pattern in ("ươ", "uô", "iê", "yê", "uê"):
        match = re.search(pattern, vie, re.IGNORECASE)
        if match:
            vowel_index = match.end() - 1
            vowel = vie[vowel_index]
            return (
                vie[:vowel_index]
                + normalize_nfc(vowel + tonal_mark)
                + vie[vowel_index + 1:]
            )

    # Vowels with inherent Vietnamese quality marks.
    match = re.search(r"[âăêôơưü]", vie, re.IGNORECASE)
    if match:
        vowel = match.group()
        return (
            vie[:match.start()]
            + normalize_nfc(vowel + tonal_mark)
            + vie[match.end():]
        )

    # Ordinary diphthongs/triphthongs: tone goes on the first vowel.
    match = re.search(r"[aeiou]", vie, re.IGNORECASE)
    if match:
        vowel = match.group()
        return (
            vie[:match.start()]
            + normalize_nfc(vowel + tonal_mark)
            + vie[match.end():]
        )

    # Final fallback.
    match = re.search(r"y", vie, re.IGNORECASE)
    if match:
        vowel = match.group()
        return (
            vie[:match.start()]
            + normalize_nfc(vowel + tonal_mark)
            + vie[match.end():]
        )

    return vie


def _convert_tonal_ast_to_vie(
    ast: list[dict],
    options: dict,
    mode: RuleMode,
) -> str:
    """Convert parsed Pinyin syllables and attach their tone marks."""

    last_syllable_idx = len(ast) - 1
    vie_parts = []
    tone_marks = {
        1: COMBINE_MACRON,
        2: COMBINE_ACUTE,
        3: COMBINE_HOOK_ABOVE,
        4: COMBINE_GRAVE,
        5: "",
    }

    for idx, syllable in enumerate(ast):
        tone = syllable.get("tone", 5)

        if tone not in tone_marks:
            raise ValueError(
                f"invalid Chinese tone: {tone!r}"
            )

        vie_syl = syllable_to_vie(
            syllable=syllable,
            options=options,
            is_last_syllable=(
                idx == last_syllable_idx
            ),
            mode=mode,
            has_following_consonant=(
                idx + 1 < len(ast)
                and bool(ast[idx + 1].get("initial"))
                and not ast[idx + 1].get("nucleus")
            ),
        )

        tone_mark = tone_marks[tone]

        if tone_mark:
            original = vie_syl
            vie_syl = add_tonal_mark_to_vowel(
                vie=vie_syl,
                tonal_mark=tone_mark,
            )

            if vie_syl == original and not re.search(
                r"[aeiouyâăêôơưü]",
                vie_syl,
                re.IGNORECASE,
            ):
                raise ValueError(
                    f"cannot apply tone {tone} to syllable {vie_syl!r}"
                )

        if idx != 0 and vie_syl:
            vie_parts.append("-")

        vie_parts.append(vie_syl)

    return "".join(vie_parts)


def pinyin_to_vie(
    pinyin: str,
    options: dict | None = None,
    *,
    mode: RuleMode,
) -> dict:
    """Parse and convert one pinyin word without IPA or stress processing."""

    options = {**(options or {}), "language": "ch"}
    _rules_for_mode(mode, "ch")

    try:
        ast = parse_pinyin(pinyin)
    except ParseError as error:
        raise ValueError(
            f"could not parse pinyin input: {pinyin!r}"
        ) from error

    vie = _convert_tonal_ast_to_vie(ast, options, mode)

    return {
        "pinyin": pinyin,
        "ast": ast,
        "vie": vie,
    }
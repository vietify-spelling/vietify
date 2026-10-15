import argparse
import logging
import re
from pathlib import Path
from typing import Literal, cast

from phonemizer import phonemize

from .converter import (
    _apply_french_liaison,
    hepburn_to_vie,
    ipa_to_vie,
    pinyin_to_vie,
)


PHONEMIZER_LANGUAGES = {
    "en-gb": "en-gb",
    "en-us": "en-us",
    "en-au": "en-au",

    "fr": "fr-fr",
    "de": "de",
    "ru": "ru",
}


def normalize_phonemized_ipa(
    ipa: str,
    language: str,
    *,
    preserve_nasalization: bool = False,
) -> str:
    # ʔ is ignored entirely: it is dropped rather than converted.
    normalized = ipa.replace("ː", "").replace('"', "").replace("ʔ", "")
    for consonant in ("n", "m", "l", "ŋ"):
        # Syllabic consonant (combining vertical line below) -> schwa + consonant.
        normalized = normalized.replace(consonant + "̩", "ə" + consonant)
    if not preserve_nasalization:
        normalized = normalized.replace("̃", "")

    if (language == "ru") :  # russian doesnt have phoneme /y/ and so on but espeak somehow use these letter
        normalized = normalized.replace("y", "ɨ")

    return (
        normalized
        # english
        .replace("ɚ", "əɹ")
        .replace("ɜ", "ə")
        .replace("ᵻ", "ɪ")
        .replace("ɾ", "r")
        # .replace("ɥ", "w")
        .replace("ʌ", "ɔ")

       #russian 
        .replace("ɭ" ,"l")
        .replace("mʲ", "mj")
        .replace("nʲ", "nj")

        .replace("tʲ", "tj")
        .replace("dʲ", "dj")
        .replace("kʲ", "kj")
        .replace("ɡʲ", "ɡj")
        .replace("pʲ", "pj")
        .replace("bʲ", "bj")
        
        .replace("fʲ", "fj")
        .replace("vʲ", "vj")
        .replace("sʲ", "sj")
        .replace("zʲ", "zj")
        .replace("ʂʲ", "ʂj")
        .replace("ʐʲ", "ʐj")   
        .replace("xʲ", "xj")

        .replace("lʲ", "lj")
        .replace("rʲ", "rj")
        

        .replace("tʃʲ", "tʃj")
        # .replace("dʒʲ", "dʒj")
        # .replace("ɕʲ", "ɕj")
        # .replace("ʑʲ", "ʑj")      

    )

OutputMode = Literal["weak", "strong", "ipa"]

LANGUAGE_CHOICES = (
    "en-gb",
    "en-us",
    "en-au",
    "fr",
    "de",
    "ru",
    "ch",
    "ja",
    "ipa",
)
MODE_CHOICES = ("weak", "strong", "ipa")

logger = logging.getLogger(__name__)

# Characters espeak emits when it cannot encode a symbol (e.g. "hamb??k").
_ESPEAK_UNDECODABLE = ("?", "�")

def text_to_vietify(
    text: str,
    language: str,
    mode: OutputMode,
) -> str:
    pronunciation = _text_to_pronunciation(text, language)

    if mode == "ipa":
        return pronunciation

    pronunciation = _normalize_pronunciation(pronunciation, language)
    return _convert_pronunciation(pronunciation, language, mode)


def text_to_vietify_all(text: str, language: str) -> tuple[str, str, str]:
    """Return (IPA, strong, weak) for text, phonemizing only once."""
    pronunciation = _text_to_pronunciation(text, language)
    normalized = _normalize_pronunciation(pronunciation, language)
    return (
        pronunciation,
        _convert_pronunciation(normalized, language, "strong"),
        _convert_pronunciation(normalized, language, "weak"),
    )


def _text_to_pronunciation(text: str, language: str) -> str:
    if language in {"ch", "ja", "ipa"}:
        return text

    return cast(
        str,
        phonemize(
            text,
            language=PHONEMIZER_LANGUAGES[language],
            backend="espeak",
            strip=True,
            preserve_punctuation=True,
            with_stress=False # espeak put stress in the middle of a syllable after the initial consonant
            # this can make things complicated for affricates/ glides ...
        ),
    )


def _normalize_pronunciation(pronunciation: str, language: str) -> str:
    if language not in {"ch", "ja"}:
        return normalize_phonemized_ipa(
            pronunciation,
            language,
            preserve_nasalization=language == "fr",
        )
    return pronunciation


def _convert_pronunciation(
    pronunciation: str,
    language: str,
    mode: Literal["weak", "strong"],
) -> str:
    converted_words = []

    if language == "ja":
        return hepburn_to_vie(pronunciation, mode=mode)["vie"]

    for word in pronunciation.split():
        match = re.match(
            r"^([^\w\u0300-\u036f]*)(.*?)([^\w\u0300-\u036f]*)$",
            word,
            re.UNICODE,
        )

        if not match or not match.group(2):
            converted_words.append({"vie": word})
            continue

        leading, pronunciation, trailing = match.groups()

        if "(" in pronunciation or ")" in pronunciation:
            logger.warning(
                "language-switch markers in %r (non-pure input); "
                "leaving token unconverted",
                word,
            )
            converted_words.append({"vie": word})
            continue

        if any(char in pronunciation for char in _ESPEAK_UNDECODABLE):
            logger.warning(
                "espeak output contains undecodable characters in %r; "
                "ignoring them",
                word,
            )
            pronunciation = "".join(
                char for char in pronunciation
                if char not in _ESPEAK_UNDECODABLE
            )
            if not pronunciation:
                converted_words.append({"vie": leading + trailing})
                continue

        if language == "ch":
            vie = pinyin_to_vie(
                pronunciation,
                mode=mode,
            )["vie"]
        else:
            results = ipa_to_vie(
                pronunciation,
                {"language": language},
                mode=mode,
            )

            if not results:
                raise ValueError(
                    f"could not convert IPA text: {pronunciation!r}"
                )

            vie = "-".join(result["vie"] for result in results)

        converted_words.append({
            "vie": leading + vie + trailing
        })

    if language == "fr":
        converted_words = _apply_french_liaison(converted_words)

    return " ".join(word["vie"] for word in converted_words)


def process_text_file(
    input_file: Path,
    output_file: Path,
    language: str,
) -> None:
    """Write IPA, strong, and weak results for every non-empty input line."""
    output_lines = []
    errors = []

    with input_file.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            text = raw_line.rstrip("\r\n")

            if not text.strip():
                continue

            # Step 1: text -> IPA
            try:
                pronunciation = _text_to_pronunciation(text, language)
            except Exception as error:
                errors.append(f"line {line_number} IPA: {error}")

                # Preserve original input.
                output_lines.extend(
                    (text, text, "", "", "\n")
                )
                continue

            # Step 2: normalize IPA
            try:
                normalized = _normalize_pronunciation(
                    pronunciation,
                    language,
                )
            except Exception as error:
                errors.append(f"line {line_number} normalization: {error}")

                # Preserve IPA even when normalization fails.
                normalized = None

            # Step 3: IPA -> Vietnamese
            results = []

            for mode in ("strong", "weak"):
                if normalized is None:
                    results.append("")
                    continue

                try:
                    results.append(
                        _convert_pronunciation(
                            normalized,
                            language,
                            mode,
                        )
                    )
                except Exception as error:
                    errors.append(
                        f"line {line_number} {mode}: {error}"
                    )

                    # Preserve IPA by leaving Vietnamese result blank.
                    results.append("")

            output_lines.extend(
                (text, pronunciation, *results, "\n")
            )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        "\n".join(output_lines) + "\n",
        encoding="utf-8",
    )

    if errors:
        raise ValueError(
            "conversion errors:\n" + "\n".join(errors)
        )
    
def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert text or IPA pronunciation to Vietnamese spelling."
        ),
    )
    parser.add_argument(
        "text",
        nargs="*",
        help=(
            "Text to convert, pinyin when --language=ch, or IPA when "
            "--language=ipa. Omit when using --input-file."
        ),
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        help="Read input text from a UTF-8 file, one test case per line.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Write IPA, strong, and weak results to this file.",
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=LANGUAGE_CHOICES,
        default="en-us",
        help=(
            "Input language: en-gb (British English), en-us (American English), "
            "en-au (Australian English), fr (French), de (German), ru (Russian), "
            "ch (Chinese pinyin), ja (Japanese Hepburn romanization), "
            "or ipa (already-transcribed IPA). "
            "Default: en-us."
        ),
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=MODE_CHOICES,
        default=None,
        help=(
            "Output mode: weak, strong, or ipa. "
            "ipa outputs the pronunciation input without Vietify conversion. "
            "Default: weak."
        ),
    )
    args = parser.parse_args()

    if args.input_file is not None:
        if args.text:
            parser.error("provide either text or --input-file, not both")
        if args.output_file is None:
            parser.error("--output-file is required with --input-file")
        if args.mode is not None:
            parser.error("--mode cannot be used with --input-file")

        try:
            process_text_file(args.input_file, args.output_file, args.language)
        except (OSError, RuntimeError, ValueError) as error:
            parser.error(str(error))
        return 0

    if args.output_file is not None:
        parser.error("--output-file requires --input-file")
    if not args.text:
        parser.error("provide text or use --input-file")

    try:
        print(
            text_to_vietify(
                " ".join(args.text),
                args.language,
                args.mode or "weak",
            )
        )
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import re
import sys
from pathlib import Path
from typing import Literal

from phonemizer import phonemize

# from .converter import ipa_to_vie
from typing import cast

if __package__:
    from .converter import _apply_french_liaison, ipa_to_vie, pinyin_to_vie
else:
    # Allow ``python main.py`` when this file is run from the package folder.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from vietify.converter import _apply_french_liaison, ipa_to_vie, pinyin_to_vie


PHONEMIZER_LANGUAGES = {
    "en-gb": "en-gb",
    "en-us": "en-us",
    "en-au": "en-au",

    "fr": "fr-fr",
    "de": "de",
    "ru": "ru", 

    # "ko": "ko",
}


def normalize_phonemized_ipa(
    ipa: str,
    language: str,
    *,
    preserve_nasalization: bool = False,
) -> str:
    normalized = ipa.replace("ː", "")
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

def text_to_vietify(
    text: str,
    language: str,
    mode: OutputMode,
) -> str:
    if language in {"ch", "ipa"}:
        pronunciation = text
    else:
        pronunciation = cast(
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

    if mode == "ipa":
        return pronunciation

    if language != "ch":
        pronunciation = normalize_phonemized_ipa(
            pronunciation,
            language,
            preserve_nasalization=language == "fr",
        )

    converted_words = []

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

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert text or IPA pronunciation to Vietnamese spelling."
        ),
    )
    parser.add_argument(
        "text",
        nargs="+",
        help=(
            "Text to convert, pinyin when --language=ch, or IPA when "
            "--language=ipa."
        ),
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=(
            "en-gb",
            "en-us",
            "en-au",
            "fr",
            "de",
            "ru",
            "ch",
            "ja",
            "ko",
            "ipa",
        ),
        default="en-us",
        help=(
            "Input language: en-gb (British English), en-us (American English), "
            "en-au (Australian English), fr (French), de (German), ru (Russian), "
            "ch (Chinese pinyin), ja (Japanese), ko (Korean), or ipa (already-transcribed IPA). "
            "Default: en-us."
        ),
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=("weak", "strong", "ipa"),
        default="weak",
        help=(
            "Output mode: weak, strong, or ipa. "
            "ipa outputs the pronunciation input without Vietify conversion. "
            "Default: weak."
        ),
    )
    args = parser.parse_args()

    try:
        print(
            text_to_vietify(
                " ".join(args.text),
                args.language,
                args.mode,
            )
        )
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

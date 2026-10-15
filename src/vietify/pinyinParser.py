import re
import unicodedata

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar(r"""
Word = ws "/"? (Syllable ws)* "/"? ws 
# Word = ws "/"? Syllable* "/"? ws
# concatenated Pinyin creates segmentation ambiguity: liang'an vs li'an
ws = " "*


Syllable =
      SyllableWithEnding
    / SyllableWithConsonant
    / SyllableBare

SyllableWithEnding =
     InitialConsonant  SyllableEnding

SyllableWithConsonant =
    InitialConsonant

SyllableBare =
     SyllableEnding

SyllableEnding =
      DiphthongWithEnding
    / VowelWithEnding
    / BareDiphthong
    / BareVowel
    
DiphthongWithEnding = (Diphthong) EndingConsonant !(Diphthong / Vowel) 
VowelWithEnding = Vowel EndingConsonant  !(Diphthong / Vowel) 

Diphthong = 
    Glide TrueDiphthong
    / Glide Vowel
    / TrueDiphthong

BareDiphthong =
    Diphthong !Vowel

BareVowel =
    Vowel

InitialConsonant =
      "zh"
    / "ch"
    / "sh"
    / "b"
    / "p"
    / "m"
    / "f"
    / "d"
    / "t"
    / "n"
    / "l"
    / "g"
    / "k"
    / "h"
    / "j"
    / "q"
    / "x"
    / "r"
    / "z"
    / "c"
    / "s"

# whatever appear in EndingConsonant or ApprxEndingConsonant needs to be mapped in ENDING_CONSONANT_MAPPING (otherwise will be mapped to null )
EndingConsonant =
      "ng"
    / "n"


Vowel =
    #fr
    "a"
    / "u"
    / "o"
    / "i"
    / "e"
    / "ê"
    / "ü"
    / "v"


Glide =
    "yu"
    / "w"
    / "y"

TrueDiphthong =
      "ei"
    / "iao"
    / "uai"
    / "ou"
    / "ai"
    / "ao"
    / "iu"
    / "ua"
    / "üa"
    / "üe"
    / "ie"
    / "io"
    / "ia"
    / "uo"
    / "ui"
    

""")




class Visitor(NodeVisitor):
    """Transform parsed pronunciation grammar nodes into structured data."""

    def visit_Word(self, node, children):
        """Return word syllables as a normalized list."""
        syllables = children[2]

        def collect_syllables(value):
            if isinstance(value, dict):
                return [value]
            if isinstance(value, (list, tuple)):
                return [
                    syllable
                    for child in value
                    for syllable in collect_syllables(child)
                ]
            return []

        return collect_syllables(syllables)

    def visit_Syllable(self, node, children):
        return children[0]


    def visit_SyllableWithEnding(self, node, children):
        consonant, ending = children

        return {
            "initial": consonant,
            "nucleus": ending["nucleus"],
            "ending": ending["ending"],
        }


    def visit_SyllableWithConsonant(self, node, children):
        consonant = children

        return {
            "initial": consonant,
            "nucleus": None,
            "ending": None,
        }


    def visit_SyllableBare(self, node, children):
        ending = children

        return {
            "initial": None,
            "nucleus": ending["nucleus"],
            "ending": ending["ending"],
        }
    
    def visit_SyllableEnding(self, node, children):
        """Return normalized syllable-ending structure."""
        child = children[0]

        if isinstance(child, dict):
            return child

        if isinstance(child, str):
            return {
                "nucleus": child,
                "ending": None,
            }

        raise TypeError(
            f"Unexpected SyllableEnding child: "
            f"{type(child).__name__}: {child!r}"
        )

    def visit_DiphthongWithEnding(self, node, children):
        nucleus, ending = children[:2]
        return {
            "nucleus": nucleus,
            "ending": ending,
        }

    def visit_VowelWithEnding(self, node, children):
        nucleus, ending = children[:2]
        return {
            "nucleus": nucleus,
            "ending": ending,
        }
    
    def visit_BareDiphthong(self, node, children):
        return {
            "nucleus": children[0],
            "ending": None,
        }


    def visit_BareVowel(self, node, children):
        return {
            "nucleus": children[0],
            "ending": None,
        }
    
    def visit_Vowel(self, node, children):
        """Return vowel text."""
        return node.text

    def visit_Diphthong(self, node, children):
        """Return diphthong text."""
        return node.text
    
    def visit_Glide(self, node, children):
        """Return glide text."""
        return node.text


    def visit_TrueDiphthong(self, node, children):
        """Return true diphthong text."""
        return node.text

    def visit_InitialConsonant(self, node, children):
        """Return initial consonant, normalizing ``kw`` stress placement."""
        text = node.text

        if text.startswith("k") and text.endswith("w"):
            stress = next(
                (c for c in text if c in "ˈˌ"),
                "",
            )
            return stress + "kw"

        return text

    def visit_EndingConsonant(self, node, children):
        """Return final consonant text."""
        return node.text

    def visit_DiphthongEnding(self, node, children):
        """Return diphthong ending text."""
        return node.text


    def visit_ws(self, node, children):
        """Return whitespace text."""
        return node.text

    def generic_visit(self, node, visited_children):
        """Collapse single-child nodes and preserve multi-child results."""
        if visited_children:
            return (
                visited_children[0]
                if len(visited_children) == 1
                else visited_children
            )
        return node.text

TONE_MARKS = {
    "ā": ("a", 1), "á": ("a", 2), "ǎ": ("a", 3), "à": ("a", 4),
    "ē": ("e", 1), "é": ("e", 2), "ě": ("e", 3), "è": ("e", 4),
    "ī": ("i", 1), "í": ("i", 2), "ǐ": ("i", 3), "ì": ("i", 4),
    "ō": ("o", 1), "ó": ("o", 2), "ǒ": ("o", 3), "ò": ("o", 4),
    "ū": ("u", 1), "ú": ("u", 2), "ǔ": ("u", 3), "ù": ("u", 4),
    "ǖ": ("ü", 1), "ǘ": ("ü", 2), "ǚ": ("ü", 3), "ǜ": ("ü", 4),
}


def strip_tone_marks(text):
    """Remove Pinyin tone marks or a numeric tone suffix."""
    numeric_tone = None
    if text and text[-1] in "012345":
        numeric_tone = int(text[-1])
        text = text[:-1]
        if numeric_tone == 0:
            numeric_tone = 5

    tone = None
    result = []

    for char in text:
        if char in TONE_MARKS:
            base, marked_tone = TONE_MARKS[char]
            if tone is not None:
                raise ValueError("a pinyin syllable can have only one tone mark")
            tone = marked_tone
            result.append(base)
        else:
            result.append(char)

    if numeric_tone is not None and tone is not None:
        raise ValueError("use either a pinyin tone mark or tone number, not both")

    tone = numeric_tone if numeric_tone is not None else tone
    return "".join(result), tone

def parse_syllable_text(text):
    """Normalize one Pinyin syllable."""
    text = text.lower()
    text, tone = strip_tone_marks(text)

    # j/q/x + u = ü
    text = re.sub(r"(?<=[jqx])u", "ü", text)

    # yu/yue/yuan/yun = ü/üe/üan/ün
    text = re.sub(r"^yue$", "üe", text)
    text = re.sub(r"^yuan$", "üan", text)
    text = re.sub(r"^yun$", "ün", text)
    text = re.sub(r"^yu$", "ü", text)

    # b/p/m/f + o = buo/puo/muo/fuo
    text = re.sub(r"^([bpmf])o$", r"\1uo", text)

    # z/c/s/zh/ch/sh/r + i = internal v
    text = re.sub(
        r"^(zh|ch|sh|[zcsr])i$",
        r"\1v",
        text,
    )

    return text, tone

def parse(text):
    """Parse pronunciation text and return structured representation."""

    text = unicodedata.normalize("NFC", text)
    result = []

    for token in text.split():
        normalized, tone = parse_syllable_text(token)
        tree = grammar.parse(normalized)
        syllables = Visitor().visit(tree)

        if tone is not None and len(syllables) != 1:
            raise ValueError(
                f"tone must be attached to one pinyin syllable: {token!r}"
            )

        for syllable in syllables:
            syllable["tone"] = tone or 5
            result.append(syllable)

    return result
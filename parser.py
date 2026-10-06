from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import unicodedata


grammar = Grammar(r"""
Word = ws "/"? Syllable* "/"? ws
ws = " "*


Syllable =
      SyllableWithEnding
    / SyllableWithConsonant
    / SyllableBare

SyllableWithEnding =
    Stress? InitialConsonant Stress? SyllableEnding

SyllableWithConsonant =
    Stress? InitialConsonant

SyllableBare =
    Stress? SyllableEnding

SyllableEnding =
      DiphthongWithEnding
    / VowelWithEnding
    / BareDiphthong
    / BareVowel
    
DiphthongWithEnding = (Diphthong) (EndingConsonant / ApprxEndingConsonant) !(Diphthong / Vowel) 
VowelWithEnding = Vowel (EndingConsonant / ApprxEndingConsonant) !(Diphthong / Vowel) 

Diphthong = 
    Glide TrueDiphthong
    / Glide Vowel
    / TrueDiphthong

BareDiphthong =
    Diphthong !Vowel

BareVowel =
    Vowel

InitialConsonant =
      "b"
    / "tʃ"
    / "tɹ"

    # german
    / "ts"
    / "pf"

    / "t"
    / "k"
    / "z"
    / "ɹ"
    / "r"
    / "s"
    / "m"
    / "f"
    / "ɡ"
    / "n"
    / "ɫ"
    / "l"
    / "j"
    / "w"
    / "p"
    / "θ"
    / "v"
    / "h"
    / "ŋ"
    / "ʃ"
    / "ʒ"
    / "dʒ"
    / "d"
    / "ð"

    # french 
    / "ɲ"
    / "ʁ"

    # german
    / "ç"
    / "x"
    / "ʔ"

    # russian
    / "ʐ" # espeak use this letter for /ʒ/ sound, but in russian it is /ʐ/
    / "ɕ"  # espeak use this letter for /ʃ/ sound, but in russian it is /ɕ/
    / "ʑ" 
    / "ɭ"

# whatever appear in EndingConsonant or ApprxEndingConsonant needs to be mapped in ENDING_CONSONANT_MAPPING (otherwise will be mapped to null )
EndingConsonant =
# very specific for vietnamese
     "t" !"ʃ"
    / "k" !(Stress? "w")
    / "p"

    / "m"
    / "n"
    / "ŋ"

# this are mostly kept as they are for 'weak vietify' and turn to an approximate one in 'strong vietify'
ApprxEndingConsonant = 
# i purposefully only choose stop consonants and l here
     "b"
    / "ɡ"
    / "d"

    / "v"
    / "f"
    / "s"
    / "z"

    / "l"
    / "ɫ"

    # french 
    / "ʁ"
    
    #german
    / "ts"
    / "pf"

    / "r"
    / "x"
    / "ç"
# other consonant are treated as seperated syllable

Vowel =
    #fr
      "ɑ̃"
    / "ɛ̃"
    / "ɔ̃"
    / "œ̃"
    / "ø"
    / "œ"
    / "y"
    ##
    / "a"
    / "ʊ"
    / "ə"
    / "ɔ"
    / "u"
    / "ɪ"
    / "o"
    / "ɛ"
    / "e"
    / "i"
    / "ɑ"
    / "ɝ"
    / "æ"

    # german
    / "ɐ"
    / "ʏ"

    # russian
    / "ɵ"
    / "ɨ"

Stress =
      "ˈ"
    / "ˌ"


Glide =
    "j"
    / "w"
    / "ɥ"

TrueDiphthong =
      "oʊ"
    / "eɪ"
    / "aɪ"
    / "ɑɪ"
    / "aʊ"
    / "əj"
    / "ɔɪ"
    / "wa"
    / "yi"

    #german
    / "aɪ"
    / "ɔʏ"


""")


def stress_value(stress):
    if stress == "ˈ":
        return 1
    if stress == "ˌ":
        return 2
    return None


def remove_stress(text):
    return text.replace("ˈ", "").replace("ˌ", "")



class Visitor(NodeVisitor):
    """Transform parsed pronunciation grammar nodes into structured data."""

    def visit_Word(self, node, children):
        """Return word syllables as a normalized list."""
        _, _, syllables, _, _ = children
        return syllables if isinstance(syllables, list) else [syllables]

    def visit_Syllable(self, node, children):
        return children[0]


    def visit_SyllableWithEnding(self, node, children):
        stress1, consonant, stress2, ending = children

        stress = stress1 or stress2

        return {
            "stress": stress_value(stress),
            "initial": remove_stress(consonant) if consonant else None,
            "nucleus": ending["nucleus"],
            "ending": ending["ending"],
        }


    def visit_SyllableWithConsonant(self, node, children):
        stress, consonant = children

        return {
            "stress": stress_value(stress),
            "initial": remove_stress(consonant) if consonant else None,
            "nucleus": None,
            "ending": None,
        }


    def visit_SyllableBare(self, node, children):
        stress, ending = children

        return {
            "stress": stress_value(stress),
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

    def visit_Stress(self, node, children):
        """Return stress marker text."""
        return node.text

    def visit_ws(self, node, children):
        """Return whitespace text."""
        return node.text

    def generic_visit(self, node, children):
        """Collapse single-child nodes and preserve multi-child results."""
        if children:
            return children[0] if len(children) == 1 else children
        return node.text

    def visit_ApprxEndingConsonant(self, node, children):
        return node.text

def parse(text):
    """Parse pronunciation text and return its structured representation."""
    text = unicodedata.normalize("NFC", text)
    tree = grammar.parse(text)
    return Visitor().visit(tree)
import unittest

from ..converter import hepburn_to_vie
from ..main import text_to_vietify


class HepburnConversionTests(unittest.TestCase):
    def test_nasal_assimilates_to_following_place(self) -> None:
        cases = {
            "sanpai": "bilabial",
            "sanbai": "bilabial",
            "sanmai": "bilabial",
            "sankai": "velar",
            "genki": "velar",
            "sannen": "alveolar",
            "sanchō": "dorso_palatal",
            "sanrui": "apical",
            "sanha": "nasalized",
            "san'ya": "nasalized",
        }

        for word, expected in cases.items():
            with self.subTest(word=word):
                result = hepburn_to_vie(word, mode="strong")
                self.assertEqual(
                    result["ast"][0]["nasal_realization"],
                    expected,
                )

    def test_nasal_assimilates_across_whitespace(self) -> None:
        self.assertEqual(
            hepburn_to_vie("san kai!", mode="strong")["vie"],
            "sang kai!",
        )

    def test_ja_text_route_uses_hepburn_without_phonemizing(self) -> None:
        self.assertEqual(
            text_to_vietify("san mai.", "ja", "weak"),
            "sam mai.",
        )

    def test_nasal_before_vowel_is_marked_nasalized(self) -> None:
        result = hepburn_to_vie("kan'i", mode="strong")
        self.assertEqual(result["ast"][0]["nasal_realization"], "nasalized")

    def test_yōon_and_y_glide_are_preserved(self) -> None:
        self.assertEqual(hepburn_to_vie("kya", mode="strong")["vie"], "kia")
        self.assertEqual(hepburn_to_vie("ya", mode="strong")["vie"], "ia")

    def test_context_sensitive_japanese_consonants(self) -> None:
        cases = {
            "sa": "sa",
            "si": "shi",
            "su": "sư",
            "se": "sê",
            "so": "sô",
            "sya": "sha",
            "syu": "shư",
            "syo": "shô",
            "za": "dza",
            "zi": "ji",
            "zu": "dzư",
            "ze": "dzê",
            "zo": "dzô",
            "zya": "ja",
            "zyu": "jư",
            "zyo": "jô",
            "ta": "ta",
            "ti": "chi",
            "tu": "tsư",
            "te": "tê",
            "to": "tô",
            "tya": "cha",
            "tyu": "chư",
            "tyo": "chô",
            "da": "đa",
            "di": "ji",
            "du": "dzư",
            "de": "đê",
            "do": "đô",
            "dya": "ja",
            "dyu": "jư",
            "dyo": "jô",
            "ha": "ha",
            "hi": "hyi",
            "hu": "phư",
            "he": "hê",
            "ho": "hô",
            "hya": "hya",
            "hyu": "hyư",
            "hyo": "hyô",
        }

        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(
                    hepburn_to_vie(source, mode="strong")["vie"],
                    expected,
                )

    def test_context_sensitive_rules_also_accept_y_spelling(self) -> None:
        cases = {
            "sya": "sha",
            "zya": "ja",
            "tya": "cha",
            "dya": "ja",
            "hya": "hya",
        }

        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(
                    hepburn_to_vie(source, mode="strong")["vie"],
                    expected,
                )

    def test_j_is_not_used_as_a_y_glide_in_hepburn(self) -> None:
        for source in ("sja", "zja", "tja", "dja", "hja"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    hepburn_to_vie(source, mode="strong")


if __name__ == "__main__":
    unittest.main()

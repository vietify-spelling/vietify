NULL_MAPPING = "_"

# many work TODO
ENDING_CONSONANT_MAPPING: dict[str, str] = {
    "n": "n",
    "n'": "n",
}

NASAL_REALIZATION_MAPPING: dict[str, str] = {
    "bilabial": "m",
    "velar": "ng",
    "dorso_palatal": "nh",
    "alveolar": "n",
    "apical": "n",
    "nasalized": "ng",
}


INITIAL_MAPPING: dict[str, str] = {
    # Plain consonants
    "b": "b",
    "p": "p",
    "m": "m",

    "f": "ph",

    "d": "đ",
    "t": "t",
    "n": "n",

    "r": "r",
    "g": "g",
    "k": "k",

    "h": "h",

    "z": "z",
    "s": "s",

    "j": "j",

    # Japanese /w/
    "w": "w",

    # Hepburn affricates / fricatives
    "sh": "sh",
    "ch": "ch",
    "ts": "ts",

    # Yōon / palatalized consonants
    "ny": "nh",
    "jy": "j",
}

CONTEXTUAL_INITIAL_MAPPING: dict[tuple[str, str], str] = {
    # /s/ is alveolo-palatal before /i/ and in the yōon series.
    ("s", "i"): "sh",
    ("sy", "a"): "sh",
    ("sy", "u"): "sh",
    ("sy", "o"): "sh",
    # /z/ has affricated realizations in these environments.
    ("z", "a"): "dz",
    ("z", "i"): "j",
    ("z", "u"): "dz",
    ("z", "e"): "dz",
    ("z", "o"): "dz",
    ("zy", "a"): "j",
    ("zy", "u"): "j",
    ("zy", "o"): "j",
    # /t/ is affricated before /i, u/ and in the yōon series.
    ("t", "i"): "ch",
    ("t", "u"): "ts",
    ("ty", "a"): "ch",
    ("ty", "u"): "ch",
    ("ty", "o"): "ch",
    # /d/ parallels /z/ in the listed voiced environments.
    ("d", "i"): "j",
    ("d", "u"): "dz",
    ("dy", "a"): "j",
    ("dy", "u"): "j",
    ("dy", "o"): "j",
    # /h/ weakens to [ç] or [ɸ] before /i, u/ and in yōon.
    ("h", "i"): "kh",
    ("h", "u"): "ph",
    ("hy", "a"): "kh",
    ("hy", "u"): "kh",
    ("hy", "o"): "kh",
}


NUCLEUS_MAPPING: dict[str, str] = {
    "a": "a",
    "i": "i",
    "u": "ư",
    "e": "ê",
    "o": "ô",

    # Long vowels
    "ā": "a:",
    "ī": "i:",
    "ū": "ư:",
    "ē": "ê:",
    "ō": "ô:",

    "ia": "ia",
    "ii": "i",
    "iu": "i-ư",
    "ie": "i-ê",
    "io": "i-ô",

    "iā": "ia:",
    "iī": "i:",
    "iū": "i-ư:",
    "iē": "i-ê:",
    "iō": "i-ô:",
}
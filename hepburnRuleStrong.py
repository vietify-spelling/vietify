NULL_MAPPING = "_"

# many work TODO
ENDING_CONSONANT_MAPPING: dict[str, str] = {
    "n": "n",
    "n'": "n",
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
    # "hy": "h",
    "my": "m",
    "ry": "r",
    "by": "b",
    "py": "p",
    "jy": "j",
    "dy": "đ",
}


NUCLEUS_MAPPING: dict[str, str] = {
    "a": "a",
    "i": "i",
    "u": "ư",
    "e": "e",
    "o": "o",

    # Long vowels
    "ā": "a",
    "ī": "i",
    "ū": "ư",
    "ē": "ê",
    "ō": "ô",
}
NULL_MAPPING = "_"

TONE_MAPPING: dict[str, str] = {
    "1": "ngang",
    "2": "sắc",
    "3": "hỏi",
    "4": "nặng",
    "5": "không",
}

ENDING_CONSONANT_MAPPING: dict[str, str] = {
    "n": "n",
    "ng": "ng",
}  


NUCLEUS_MAPPING: dict[str, str] = {
    "v": "ơr",
    "ü": "ü",
    "u": "u",
    "i": "i",  # i can be [ɹ̩~ɻ̩] following z-, c-, s-, zh-, ch-, sh- or r-
    "a": "a",
    "ê": "e",
    "o": "o",
    "e": "ơ",

    "yi" : "i",
    "wu": "wu",
    "yu" : "ü",

    "ei": "ây",  # not exactly, vietnamese ây is [ʌj]
    "ou": "âu",  # not exactly, vietnamese âu ís  [ʌw]
    "ai": "ai",
    "ao": "ao",
    "iu": "jâu",
    "ua": "oa",
    "üa": "ü-e",
    "üe": "ü-ê",
    

    "ye" : "jê",
    "ie" : "jê",

    "yo": "jô",
    "io": "jô",

    "you": "jâu",
    
    "ya": "ja",
    "ia": "ja",

    "yao": "jao",
    "iao": "jao",

    "wo": "wô",
    "uo": "wô",

    "wei": "wây",

    "ui": "uay",

    "wa": "wa",
    
    "wai": "wai",
    "uai": "oai",

    "yue": "ü-ê",
}

SYLLABLE_ENDING_MAPPING: dict[str, str] = {
    **NUCLEUS_MAPPING,
    **{
        nucleus + ending: mapped_nucleus + mapped_ending
        for nucleus, mapped_nucleus in NUCLEUS_MAPPING.items()
        for ending, mapped_ending in ENDING_CONSONANT_MAPPING.items()
    },

    "yin": "in",
    "ying": "inh",

    "ong": "ung",
    "yong": "jung",
    "iong": "jung",

    "yan": "jen",
    "ian": "iên",


    "wen": "wân",
    "un": "uân",
    "weng": "wâng",

    "yuan": "ü-en",
    # "üan": "ü-en",
}


LETTER_MAPPING: dict[str, str] = {
    "b": "b",
    "p": "p",
    "m": "m",
    "f": "ph",
    "d": "t",
    "t": "th",
    "n": "n",
    "l": "l",
    "g": "g",
    "k": "k",
    "h": "kh",
    "j": "tr",
    "q": "trh",
    "x": "s",
    "zh": "ch",
    "ch": "chh",
    "sh": "sh",
    "r": "r",
    "z": "ts",
    "c": "tsh",
    "s": "x",
    "ng": "ng",

    "ü": "ü",
    "u": "u",
    "i": "i",
    "a": "a",
    "ê": "e",
    "o": "o",
    "e": "ơ",
    "v": "ơr",
}




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
    "ü": "uy",
    "u": "u",
    "i": "i",  # i can be [ɹ̩~ɻ̩] following z-, c-, s-, zh-, ch-, sh- or r-
    "a": "a",
    "ê": "e",
    "o": "o",
    "e": "ơ",

    "yi" : "i",
    "wu": "u",
    "yu" : "uy",

    "ei": "ây",  # not exactly, vietnamese ây is [ʌj]
    "ou": "âu",  # not exactly, vietnamese âu ís  [ʌw]
    "ai": "ai",
    "ao": "ao",
    "iu": "i-âu",
    "ua": "oa",
    "üa": "uy-e",
    "üe": "uy-ê",
    

    "ye" : "i-ê",
    "ie" : "ia",

    "yo": "i-ô",
    "io": "i-ô",

    "you": "i-âu",
    
    "ya": "i-a",
    "ia": "ia",

    "yao": "i-ao",
    "iao": "iêu",

    "wo": "wô",
    "uo": "ua",

    "wei": "wây",

    "ui": "uay",

    "wa": "wa",
    
    "wai": "wai",
    "uai": "oai",

    "yue": "uy-ê",
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
    "yong": "i-ung",
    "iong": "i-ung",

    "yan": "i-en",
    "ian": "iên",


    "wen": "wân",
    "un": "uân",
    "weng": "wâng",

    "yuan": "ü-en",
    # "üan": "ü-en",

    #specific to strong mode
    "ien" : "iên",
    "ieng" : "iêng",
    "ian" : "iên",
    "iang" : "iêng",

    # "uon": "uôn",
    # "uong": "uông",
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
    "q": "tr",
    "x": "s",
    "zh": "ch",
    "ch": "ch",
    "sh": "sh",
    "r": "r",
    "z": "ts",
    "c": "ts",
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




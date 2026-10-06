NULL_MAPPING = "_"

ENDING_CONSONANT_MAPPING: dict[str, str] = {
    "t": "t",
    "d": "t",
    "k": "c",
    "ɡ": "c",
    "p": "p",
    "b": "p",


    "m": "m",
    "n": "n",
    "ŋ": "ng",


    "v": "p",
    "f" : "p",
    "s" : "t",
    "z" : "t",

    "l": "l",
    "ɫ": "l",

    "ʁ": "ʁ",

    #german
    "x": "c",
    "ç": "c",

    "ts": "t",
    "pf": "p",
    "r" : "r"
} 


NUCLEUS_MAPPING: dict[str, str] = {
    # exact 1-1 correspondant
    "a": "a",
    "aɪ": "ai",
    "e": "ê",
    "eɪ": "ây",
    "i": "i",
    "iɛ": "ia",
    "o": "o",
    "oʊ": "âu",
    "u": "u",
    "uɛ": "oe", ##
    "ɔ": "o",
    "ɔɪ": "oi",
    "ə": "ơ",
    "əj": "ơi",
    "ɛ": "e",

    "ɨ": "ư",
 

    # not exact equivalence in vietnamese 
    "aʊ": "ao",
    "yi": "ui",

    #german
    "ɔʏ": "oi",

    # "j": "i",
    "jaʊ": "iau",
    "jeɪ": "iây",
    "ji": "i",
    "joʊ": "iau",
    "ju": "iu",
    "jæ": "iae",
    "jɑ": "ia",
    "jɔ": "io",
    "jə": "ia",
    "jɛ": "iê",
    "jɪ": "i",
    "jʊ": "iu",

    "waʊ": "uau",
    "weɪ": "uây",
    "wi": "ui",
    "woʊ": "uâu",
    "wu": "u",
    "wæ": "ua",
    "wɑ": "ua",
    "wɔ": "uo",
    "wə": "ua",
    "wɛ": "uê",
    "wɪ": "ui",
    "wʊ": "u",
    "wa": "oa",

    "ɥi": "uy",
    "ɥɛ": "uy-e",
    "ɥe": "uy-ê",
    "ɥɛ̃": "uy-ăng",
    "ɥa": "uya",
    "ɥɑ": "uya",
    "ɥɔ": "uy-o",
    "ɥœ": "uya",
    "ɥø": "uya",

    "æ": "a",
    "ɑ": "a",
    "ɑɛ": "a",

    #very similar to /i/ and /u/ /y/ just mostly length, slightly less forward/backward
    "ɪ": "i",
    "ʊ": "u",
    "ʏ": "uy",

    "y": "uy",
    "ø": "ơ",
    "œ": "ơ",
    "ɐ": "ơ",

    "ɑ̃": "oong",
    "ɛ̃": "ăng",
    "ɔ̃": "ông",
    "œ̃": "ăng",

    "jɑ̃": "i-oong",
    "jɛ̃": "i-ăng",
    "jɔ̃": "i-ông",
    "jœ̃": "i-ăng",

    # russian
    "ɵ": "ô"

}


SYLLABLE_ENDING_MAPPING: dict[str, str] = {
    **NUCLEUS_MAPPING,
    **{
        nucleus + ending: mapped_nucleus + mapped_ending
        for nucleus, mapped_nucleus in NUCLEUS_MAPPING.items()
        for ending, mapped_ending in ENDING_CONSONANT_MAPPING.items()
    },

    # ia/ja + ending → iê + mapped ending
    **{
        nucleus + ending: "iê" + mapped_ending
        for nucleus in ("ia", "ja", "jə", "iə")
        for ending, mapped_ending in ENDING_CONSONANT_MAPPING.items()
    },

    # ua/wa + ending → uô + mapped ending
    **{
        nucleus + ending: "uô" + mapped_ending
        for nucleus in ("uə", "wə")
        for ending, mapped_ending in ENDING_CONSONANT_MAPPING.items()
    },

    # uỵa + ending → uyệ + mapped ending
    **{
        nucleus + ending: "uô" + mapped_ending
        for nucleus in ("wiə", "ya", "yə", "yɐ")
        for ending, mapped_ending in ENDING_CONSONANT_MAPPING.items()
    },

    # Overrides
    "ɔŋ": "oong", 
    "jəŋ": "iêng",

    #  rule : ich/ac
    "ec": "ach",
    "êc": "êch",
    "ic": "ich",
    "yc": "ych",
    "oec" : "oach",
    "uêc" : "uêch",
    "uyc" : "uych",

}

LETTER_MAPPING: dict[str, str] = {
    # exact 1-1 correspondant
    " ": "",
    ",": "",
    "/": "",
    # "ˈ": " ",
    "ˈ": "",
    "ˌ": "",

    # t aspiration rule
   "tˈ": "th",         #stress mark position produced by espeak is weird
    "tˌ": "th",
    "ˈt": "th",         #stress mark position produced by espeak is weird
    "ˌt": "th",
    "t": "t",  

    "a": "a",
    "b": "b",
    "d": "đ",
    "e": "e",
    "o": "ô",
    "f": "ph",
    "h": "h",
    "i": "i",
    "k": "k",
    # "kw": "qu",
    "m": "m",
    "n": "n",
    "p": "p",
    "s": "x",
    "tʃ": "ch",
    "u": "u",
    "v": "v",
    "w": "w",
    "ŋ": "ng",

    "ɔ": "o",
    "ə": "ơ",
    "ɛ": "ê",
    "l": "l",

    "tɹ": "tr",

    "z": "z",
    "r": "r",

    # french
    "ɲ": "nh",



    # not exact equivalence in vietnamese 
    "dʒ": "gi",
    "ʒ": "gi",  ##gi
    "j": "gi",
 
    "æ": "a",
    "ɑ": "a",
    "ɪ": "i",
    "ʊ": "u",
    "ɝ": "ơ",

    "ɡ": "ɡ",
    "ɫ": "l",
    "ɹ": "r",
    "ʃ": "sh",
    "θ": "s",
    "ð": "z",

    # french
    "y": "uy",
    "ɥ": "uy",

    "ɑ̃": "oong",
    "ɛ̃": "ăng",
    "ɔ̃": "ông",
    "œ̃": "ăng",

    "ø": "ơ",
    "œ": "ơ",

    "ʁ": "ɡ",

    #german
    "ʏ": "uy",
    "ɐ": "ơ",
    "x": "kh",
    "ç": "kh",
    "ts": "s",
    "pf": "ph",

    # russian
    "ʐ" : "zh",  # espeak use this letter for /ʒ/ sound, but in russian it is /ʐ/
    "ɕ" : "sh",  # espeak use this letter for /ʃ/ sound, but in russian it is /ɕ/
    "ʑ" : "zh",
    # "ɭ" : "l",

    "ɨ": "ư",
    "ɵ": "ô"
}

GERMAN_R_VOCALIZATION: dict[str, str] = {
    # German R-vocalization
    "ɪr": "iê",  # become "ia" if behind have nothing else
    "ir": "iê", # become "ia" if behind have nothing else

    "ʏr": "uyê", # become "üa" if behind have nothing else
    "yr": "uyê", # become "üa" if behind have nothing else  #make it "uya/uyê" in the strong version

    "ʊr": "ươ", # become "ưa" if behind have nothing else
    "ur": "uô", # become "ua" if behind have nothing else

    "ɛr": "e",
    "er": "ê",

    "œr": "ơ",
    "ør": "ơ",

    "ɔr": "o",
    "or": "ô",

    "ar": "a",
}

GERMAN_R_VOCALIZATION_WITHOUT_CODA: dict[str, str] = {
    "ɪr": "ia",
    "ir": "ia",
    "ʏr": "uya", 
    "yr": "uya", 
    "ʊr": "ưa", 
    "ur": "ua", 
}


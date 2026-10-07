NULL_MAPPING = "_"


ENDING_CONSONANT_MAPPING: dict[str, str] = {
    "t": "t",
    "d": "d",
    "k": "c",
    "ɡ": "ɡ",
    "p": "p",
    "b": "b",

    "m": "m",
    "n": "n",
    "ŋ": "ng",


    "v": "v",
    "f" : "f",
    "s" : "s",
    "z" : "z",

    "l": "l",
    "ɫ": "l",

    "ʁ": "ʁ",

    #german
    "x": "kh",
    "ç": "kh",

    "ts": "ts",
    "pf": "pf",
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
    "ɒ" : "o",

    "ɨ": "ư",
 

    # not exact equivalence in vietnamese 
    "aʊ": "ao",
    "yi": "üi",

    #german
    "ɔʏ": "oi",

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
    "wæ": "uae",
    "wɑ": "ua",
    "wɔ": "uo",
    "wə": "ua",
    "wɛ": "uê",
    "wɪ": "ui",
    "wʊ": "u",
    "wa": "oa",

    "ɥi": "ü-i",
    "ɥɛ": "ü-e",
    "ɥe": "ü-ê",
    "ɥɛ̃": "ü-ăng",
    "ɥa": "ü-a",
    "ɥɑ": "ü-a",
    "ɥɔ": "ü-o",
    "ɥœ": "ü-ơ",
    "ɥø": "ü-ơ",

    "æ": "ae",
    "ɑ": "ä",
    "ɑɛ": "ae",

    #very similar to /i/ and /u/ /y/ just mostly length, slightly less forward/backward
    "ɪ": "i",
    "ʊ": "u",
    "ʏ": "ü",

    "y": "ü",
    "ø": "ø",
    "œ": "œ",
    "ɐ": "â",

    "ɑ̃": "oong",
    "ɛ̃": "ăng",
    "ɔ̃": "ông",
    "œ̃": "ăng",

    "jɑ̃": "ioong",
    "jɛ̃": "iăng",
    "jɔ̃": "iông",
    "jœ̃": "iăng",

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
        for nucleus in ["wiə"]
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
    "ɒ" : "o",
    "b": "b",
    "d": "đ",
    "e": "ê",
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
    "ɛ": "e",
    "l": "l",

    "tɹ": "tr",

    "z": "z",
    "r": "r",

    # french
    "ɲ": "nh",



    # not exact equivalence in vietnamese 
    "dʒ": "dʒ",
    "ʒ": "ʒ",  ##gi
    "j": "j",
 
    "æ": "ae",
    "ɑ": "ä",
    "ɪ": "i",
    "ʊ": "u",
    "ɝ": "ơr",

    "ɡ": "ɡ",
    "ɫ": "l",
    "ɹ": "r",
    "ʃ": "sh",
    "θ": "ss",
    "ð": "zz",

    # french
    "y": "ü",
    "ɥ": "ü",

    "ɑ̃": "oong",
    "ɛ̃": "ăng",
    "ɔ̃": "ông",
    "œ̃": "ăng",

    "ø": "ø",
    "œ": "œ",

    "ʁ": "ʁ",  # this has a voiceless complementation at end of sentence/ before or after voiceless obstruent. but hard and costly to encode this...

    #german
    "ʏ": "ü",
    "ɐ": "â",
    "x": "kh",
    "ç": "kh",
    "ts": "ts",
    "pf": "pf",

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

    "ʏr": "üê", # become "üa" if behind have nothing else
    "yr": "üê", # become "üa" if behind have nothing else  #make it "uya/uyê" in the strong version

    "ʊr": "ươ", # become "ưa" if behind have nothing else
    "ur": "uô", # become "ua" if behind have nothing else

    "ɛr": "eơ",
    "er": "êơ",

    "œr": "œơ",
    "ør": "øơ",

    "ɔr": "oơ",
    "or": "ôơ",

    "ar": "aơ",
}

GERMAN_R_VOCALIZATION_WITHOUT_CODA: dict[str, str] = {
    "ɪr": "ia",
    "ir": "ia",
    "ʏr": "üa", 
    "yr": "üa", 
    "ʊr": "ưa", 
    "ur": "ua", 
}

import re
import unicodedata

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


grammar = Grammar(r"""
Word = ws "/"? (Syllable ws)* "/"? ws

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


# ---------------------------------------------------------
# Japanese Hepburn initial consonants
# ---------------------------------------------------------
#
# Multi-character consonants must come first.
#
# Examples:
#   sh + a = sha
#   ch + a = cha
#   ts + u = tsu
#   ky + a = kya
#   ry + o = ryo
#

InitialConsonant =
      "sh"
    / "ch"
    / "ts"
    # / "ky"
    # / "gy"
    / "ny"
    # / "hy"
    # / "my"
    # / "ry"
    # / "by"
    # / "py"
    / "jy"
    # / "dy"
    / "b"
    / "p"
    / "m"
    / "f"
    / "d"
    / "t"
    / "n"
    / "r"
    / "g"
    / "k"
    / "h"
    / "j"
    / "z"
    / "s"
    / "w"
    / "y"


# ---------------------------------------------------------
# Japanese moraic nasal
# ---------------------------------------------------------
#
# Hepburn:
#   n
#   n'
#
# n' prevents ambiguity before vowels/y:
#   kan'i
#   shin'yō
#
# ---------------------------------------------------------

EndingConsonant =
      "n'" 
    / "n"


# ---------------------------------------------------------
# Vowels
# ---------------------------------------------------------
#
# Macrons are canonical Hepburn representations of long vowels.
#
# ā ī ū ē ō
#
# Bare u/o etc. remain normal vowels.
# ---------------------------------------------------------

Vowel =
      "ā"
    / "ī"
    / "ū"
    / "ē"
    / "ō"
    / "a"
    / "i"
    / "u"
    / "e"
    / "o"


# ---------------------------------------------------------
# Glides
# ---------------------------------------------------------

Glide =
      "y"
    / "w"


# ---------------------------------------------------------
# True diphthongs / vowel combinations
# ---------------------------------------------------------
#
# Japanese yōon:
#
# kya kyu kyo
# gya gyu gyo
# sha shu sho
# cha chu cho
# ja  ju  jo
# nya nyu nyo
# hya hyu hyo
# bya byu byo
# pya pyu pyo
# mya myu myo
# rya ryu ryo
#
# These are represented as:
#
#   InitialConsonant + Diphthong
#
# while simple vowel sequences are handled separately.

# japanses doesnt have true diphthong tho. but i still use this representation for the sake of convenient
# ---------------------------------------------------------

TrueDiphthong =
      "ai"
    / "oi"
    / "ui"
    / "ei"
    / "au"
    / "ou"


""")
"""
ENCODING FUNCTIONS

Each encoding: f(text) -> bitstring

Based on Arabic letter properties.
"""

import re

# Arabic letter range
ARABIC_LETTERS = re.compile(r'[\u0621-\u064A]')

# Remove diacritics
DIACRITICS = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics."""
    return DIACRITICS.sub('', text)


def extract_letters(text: str) -> str:
    """Extract only Arabic letters."""
    return ''.join(ARABIC_LETTERS.findall(strip_diacritics(text)))


# ============================================================
# ENCODING 1: DOTTED vs UNDOTTED (nuqta)
# ============================================================

# Letters WITH dots (nuqta)
DOTTED = set('بتثجخذزشضظغفقنيء')
# Letters WITHOUT dots
UNDOTTED = set('احدرسصطعكلمهوى')

def encode_dotted(text: str) -> str:
    """
    Dotted letters = 1, Undotted = 0

    Hypothesis: Dots carry semantic/phonological information
    that creates structure beyond randomness.
    """
    result = []
    for char in extract_letters(text):
        if char in DOTTED:
            result.append('1')
        elif char in UNDOTTED:
            result.append('0')
        # Skip letters not in either set
    return ''.join(result)


# ============================================================
# ENCODING 2: SOLAR vs LUNAR (shamsiyya/qamariyya)
# ============================================================

# Solar letters (assimilate with definite article al-)
SOLAR = set('تثدذرزسشصضطظلن')
# Lunar letters (don't assimilate)
LUNAR = set('ابجحخعغفقكمهوي')

def encode_solar_lunar(text: str) -> str:
    """
    Solar letters = 1, Lunar = 0

    Hypothesis: Solar/lunar distinction affects phonological
    patterns that create structure.
    """
    result = []
    for char in extract_letters(text):
        if char in SOLAR:
            result.append('1')
        elif char in LUNAR:
            result.append('0')
    return ''.join(result)


# ============================================================
# ENCODING 3: VOICED vs UNVOICED
# ============================================================

# Voiced consonants (vibrating vocal cords)
VOICED = set('بدذرزضظعغلمنوي')
# Unvoiced consonants
UNVOICED = set('تثحخسشصطفقكهء')

def encode_voiced(text: str) -> str:
    """
    Voiced = 1, Unvoiced = 0

    Hypothesis: Voicing patterns create phonological structure.
    """
    result = []
    for char in extract_letters(text):
        if char in VOICED:
            result.append('1')
        elif char in UNVOICED:
            result.append('0')
    return ''.join(result)


# ============================================================
# ENCODING 4: EMPHATIC vs NON-EMPHATIC
# ============================================================

# Emphatic consonants (pharyngealized)
EMPHATIC = set('صضطظقخغعح')
# Non-emphatic
NON_EMPHATIC = set('سدتذكجشزفثبنملرويها')

def encode_emphatic(text: str) -> str:
    """
    Emphatic = 1, Non-emphatic = 0

    Hypothesis: Emphatic sounds cluster semantically.
    """
    result = []
    for char in extract_letters(text):
        if char in EMPHATIC:
            result.append('1')
        elif char in NON_EMPHATIC:
            result.append('0')
    return ''.join(result)


# ============================================================
# ENCODING 5: LETTER POSITION IN ALPHABET
# ============================================================

# First half of Arabic alphabet (by traditional order)
FIRST_HALF = set('ابتثجحخدذرزس')
# Second half
SECOND_HALF = set('شصضطظعغفقكلمنهوي')

def encode_alphabet_half(text: str) -> str:
    """
    First half of alphabet = 0, Second half = 1

    Hypothesis: Arbitrary baseline - should show NO structure
    beyond what language statistics produce.
    """
    result = []
    for char in extract_letters(text):
        if char in FIRST_HALF:
            result.append('0')
        elif char in SECOND_HALF:
            result.append('1')
    return ''.join(result)


# ============================================================
# ALL ENCODINGS
# ============================================================

ENCODINGS = {
    'dotted': (encode_dotted, "Dotted(1) vs Undotted(0) letters"),
    'solar_lunar': (encode_solar_lunar, "Solar(1) vs Lunar(0) letters"),
    'voiced': (encode_voiced, "Voiced(1) vs Unvoiced(0) consonants"),
    'emphatic': (encode_emphatic, "Emphatic(1) vs Non-emphatic(0)"),
    'alphabet_half': (encode_alphabet_half, "First(0) vs Second(1) half of alphabet"),
}


def get_encoding(name: str):
    """Get encoding function by name."""
    if name not in ENCODINGS:
        raise ValueError(f"Unknown encoding: {name}. Available: {list(ENCODINGS.keys())}")
    return ENCODINGS[name][0]


def list_encodings():
    """List all available encodings."""
    return {name: desc for name, (_, desc) in ENCODINGS.items()}

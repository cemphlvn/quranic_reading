"""
ORDINAL ENCODING FUNCTIONS

Map letters to their alphabetical position (1-28) and encode as binary.

PRE-REGISTERED HYPOTHESES:
1. ordinal_parity: Even/odd position in alphabet = arbitrary baseline (expect NO structure)
2. ordinal_high_low: First/second half by position (same as alphabet_half)
3. ordinal_bits: Full 5-bit ordinal representation → tests if letter ORDER matters

These are NOT gematria:
- We're NOT summing values
- We're testing SEQUENCE patterns via compression
- We're comparing against word_perm null
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
# ARABIC ALPHABET ORDINAL MAPPING
# ============================================================

# Standard Arabic alphabet order (Abjadi order)
# This is the TRADITIONAL order used in abjad numerals
ABJAD_ORDER = [
    'ا',  # alif - 1
    'ب',  # ba - 2
    'ج',  # jim - 3
    'د',  # dal - 4
    'ه',  # ha - 5
    'و',  # waw - 6
    'ز',  # zayn - 7
    'ح',  # ha - 8
    'ط',  # ta - 9
    'ي',  # ya - 10
    'ك',  # kaf - 11
    'ل',  # lam - 12
    'م',  # mim - 13
    'ن',  # nun - 14
    'س',  # sin - 15
    'ع',  # ayn - 16
    'ف',  # fa - 17
    'ص',  # sad - 18
    'ق',  # qaf - 19
    'ر',  # ra - 20
    'ش',  # shin - 21
    'ت',  # ta - 22
    'ث',  # tha - 23
    'خ',  # kha - 24
    'ذ',  # dhal - 25
    'ض',  # dad - 26
    'ظ',  # za - 27
    'غ',  # ghayn - 28
]

# Modern Arabic alphabet order (Hijā'ī order)
# Used in modern dictionaries
HIJAI_ORDER = [
    'ا',  # alif - 1
    'ب',  # ba - 2
    'ت',  # ta - 3
    'ث',  # tha - 4
    'ج',  # jim - 5
    'ح',  # ha - 6
    'خ',  # kha - 7
    'د',  # dal - 8
    'ذ',  # dhal - 9
    'ر',  # ra - 10
    'ز',  # zayn - 11
    'س',  # sin - 12
    'ش',  # shin - 13
    'ص',  # sad - 14
    'ض',  # dad - 15
    'ط',  # ta - 16
    'ظ',  # za - 17
    'ع',  # ayn - 18
    'غ',  # ghayn - 19
    'ف',  # fa - 20
    'ق',  # qaf - 21
    'ك',  # kaf - 22
    'ل',  # lam - 23
    'م',  # mim - 24
    'ن',  # nun - 25
    'ه',  # ha - 26
    'و',  # waw - 27
    'ي',  # ya - 28
]

# Create lookup dictionaries
ABJAD_TO_ORD = {letter: i+1 for i, letter in enumerate(ABJAD_ORDER)}
HIJAI_TO_ORD = {letter: i+1 for i, letter in enumerate(HIJAI_ORDER)}

# Handle hamza and alif variants
LETTER_NORMALIZE = {
    'ء': 'ا',  # hamza → alif
    'أ': 'ا',  # alif with hamza above → alif
    'إ': 'ا',  # alif with hamza below → alif
    'آ': 'ا',  # alif madda → alif
    'ى': 'ي',  # alif maqsura → ya
    'ة': 'ه',  # ta marbuta → ha
}


def normalize_letter(char: str) -> str:
    """Normalize letter variants."""
    return LETTER_NORMALIZE.get(char, char)


def get_ordinal_abjad(char: str) -> int:
    """Get letter's ordinal in Abjadi order (1-28)."""
    char = normalize_letter(char)
    return ABJAD_TO_ORD.get(char, 0)


def get_ordinal_hijai(char: str) -> int:
    """Get letter's ordinal in Hijā'ī order (1-28)."""
    char = normalize_letter(char)
    return HIJAI_TO_ORD.get(char, 0)


# ============================================================
# ENCODING 1: ORDINAL PARITY (Even/Odd)
# ============================================================

def encode_ordinal_parity_abjad(text: str) -> str:
    """
    Odd position = 0, Even position = 1 (Abjadi order)

    HYPOTHESIS: This is ARBITRARY. Expect NO structure beyond word-level.
    Should be our negative control.
    """
    result = []
    for char in extract_letters(text):
        ordinal = get_ordinal_abjad(char)
        if ordinal > 0:
            result.append('1' if ordinal % 2 == 0 else '0')
    return ''.join(result)


def encode_ordinal_parity_hijai(text: str) -> str:
    """
    Odd position = 0, Even position = 1 (Hijā'ī order)

    HYPOTHESIS: Different ordering, same principle. Should also show NO structure.
    """
    result = []
    for char in extract_letters(text):
        ordinal = get_ordinal_hijai(char)
        if ordinal > 0:
            result.append('1' if ordinal % 2 == 0 else '0')
    return ''.join(result)


# ============================================================
# ENCODING 2: HIGH/LOW (Above/Below median)
# ============================================================

def encode_ordinal_high_low_abjad(text: str) -> str:
    """
    Position 1-14 = 0, Position 15-28 = 1 (Abjadi order)

    HYPOTHESIS: Arbitrary split. No expected structure beyond word-level.
    """
    result = []
    for char in extract_letters(text):
        ordinal = get_ordinal_abjad(char)
        if ordinal > 0:
            result.append('1' if ordinal > 14 else '0')
    return ''.join(result)


def encode_ordinal_high_low_hijai(text: str) -> str:
    """
    Position 1-14 = 0, Position 15-28 = 1 (Hijā'ī order)
    """
    result = []
    for char in extract_letters(text):
        ordinal = get_ordinal_hijai(char)
        if ordinal > 0:
            result.append('1' if ordinal > 14 else '0')
    return ''.join(result)


# ============================================================
# ENCODING 3: FULL ORDINAL (5-bit binary per letter)
# ============================================================

def encode_ordinal_5bit_abjad(text: str) -> str:
    """
    Each letter → 5-bit binary of its Abjadi ordinal (01-28)

    HYPOTHESIS: Preserves full ordinal information.
    Tests if letter ORDER contains compressible structure.
    This is the most information-rich ordinal encoding.
    """
    result = []
    for char in extract_letters(text):
        ordinal = get_ordinal_abjad(char)
        if ordinal > 0:
            # 5 bits can encode 0-31, we use 1-28
            result.append(format(ordinal, '05b'))
    return ''.join(result)


def encode_ordinal_5bit_hijai(text: str) -> str:
    """
    Each letter → 5-bit binary of its Hijā'ī ordinal (01-28)
    """
    result = []
    for char in extract_letters(text):
        ordinal = get_ordinal_hijai(char)
        if ordinal > 0:
            result.append(format(ordinal, '05b'))
    return ''.join(result)


# ============================================================
# ENCODING 4: ORDINAL DELTA (difference from previous)
# ============================================================

def encode_ordinal_delta_sign(text: str) -> str:
    """
    Encode the SIGN of ordinal changes: up=1, down/same=0

    HYPOTHESIS: Tests if there's pattern in letter-to-letter transitions.
    Rising vs falling patterns in alphabet position.
    """
    letters = extract_letters(text)
    if len(letters) < 2:
        return ''

    result = []
    prev_ord = get_ordinal_abjad(letters[0])

    for char in letters[1:]:
        curr_ord = get_ordinal_abjad(char)
        if curr_ord > 0 and prev_ord > 0:
            delta = curr_ord - prev_ord
            result.append('1' if delta > 0 else '0')
            prev_ord = curr_ord

    return ''.join(result)


# ============================================================
# ALL ORDINAL ENCODINGS
# ============================================================

ORDINAL_ENCODINGS = {
    'ord_parity_abjad': (encode_ordinal_parity_abjad,
        "Even(1)/Odd(0) position in Abjadi alphabet order"),
    'ord_parity_hijai': (encode_ordinal_parity_hijai,
        "Even(1)/Odd(0) position in Hijā'ī alphabet order"),
    'ord_high_low_abjad': (encode_ordinal_high_low_abjad,
        "First half(0)/Second half(1) by Abjadi position"),
    'ord_high_low_hijai': (encode_ordinal_high_low_hijai,
        "First half(0)/Second half(1) by Hijā'ī position"),
    'ord_5bit_abjad': (encode_ordinal_5bit_abjad,
        "5-bit binary ordinal (Abjadi order)"),
    'ord_5bit_hijai': (encode_ordinal_5bit_hijai,
        "5-bit binary ordinal (Hijā'ī order)"),
    'ord_delta_sign': (encode_ordinal_delta_sign,
        "Sign of ordinal change: rising(1) vs falling(0)"),
}


def get_ordinal_encoding(name: str):
    """Get ordinal encoding function by name."""
    if name not in ORDINAL_ENCODINGS:
        raise ValueError(f"Unknown ordinal encoding: {name}")
    return ORDINAL_ENCODINGS[name][0]


def list_ordinal_encodings():
    """List all ordinal encodings with descriptions."""
    return {name: desc for name, (_, desc) in ORDINAL_ENCODINGS.items()}

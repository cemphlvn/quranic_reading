"""
f_dot: Morphological Encoding

f_dot(letter) = 1 if letter has dots (nuqat), else 0

Hypothesis: Dotted letters mark semantic weight/existence.
            Undotted letters mark abstraction/void.
"""

# Letter classifications
# Dotted letters (have nuqat): 1
# Undotted letters: 0

DOTTED = set('بتثجخذزشضظغفقني')
UNDOTTED = set('احدرسصطعكلمهوءةىئؤإأآ')

# Extended mapping for all variants
DOT_MAP = {
    # Dotted (1)
    'ب': 1, 'ت': 1, 'ث': 1, 'ج': 1, 'خ': 1,
    'ذ': 1, 'ز': 1, 'ش': 1, 'ض': 1, 'ظ': 1,
    'غ': 1, 'ف': 1, 'ق': 1, 'ن': 1, 'ي': 1,

    # Undotted (0)
    'ا': 0, 'ح': 0, 'د': 0, 'ر': 0, 'س': 0,
    'ص': 0, 'ط': 0, 'ع': 0, 'ك': 0, 'ل': 0,
    'م': 0, 'ه': 0, 'و': 0,

    # Hamza variants (undotted base)
    'ء': 0, 'أ': 0, 'إ': 0, 'آ': 0, 'ؤ': 0, 'ئ': 0,

    # Special forms
    'ة': 0,  # ta marbuta (undotted in most scripts)
    'ى': 0,  # alif maqsura
}


def encode_letter(letter: str) -> str:
    """Encode single letter to bit."""
    return str(DOT_MAP.get(letter, ''))


def encode_text(text: str) -> str:
    """
    Encode full text to bitstring using f_dot.

    Args:
        text: Arabic text (with or without diacritics)

    Returns:
        Bitstring where 1=dotted, 0=undotted
    """
    import re
    # Strip diacritics
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    clean = diacritics.sub('', text)

    # Encode each letter
    bits = []
    for char in clean:
        if char in DOT_MAP:
            bits.append(str(DOT_MAP[char]))

    return ''.join(bits)


def encode_word(word: str) -> str:
    """Encode single word."""
    return encode_text(word)


def density(text: str) -> float:
    """Compute dot-density of text."""
    bits = encode_text(text)
    if not bits:
        return 0.0
    return bits.count('1') / len(bits)


def get_stats() -> dict:
    """Return encoding statistics."""
    dotted = sum(1 for v in DOT_MAP.values() if v == 1)
    undotted = sum(1 for v in DOT_MAP.values() if v == 0)
    return {
        "encoding": "f_dot",
        "description": "1 if letter has dots, 0 otherwise",
        "dotted_letters": dotted,
        "undotted_letters": undotted,
        "baseline_density": dotted / (dotted + undotted)
    }


if __name__ == "__main__":
    # Test
    test = "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ"
    print(f"Text: {test}")
    print(f"Encoded: {encode_text(test)}")
    print(f"Density: {density(test):.2%}")
    print(f"Stats: {get_stats()}")

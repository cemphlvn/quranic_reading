"""
f_root: Root Letter Encoding (Simplified)

Arabic words are built from 3-4 letter roots.
Root letters carry core meaning; pattern letters are grammatical.

f_root(letter) = 1 if letter is "heavy" (common root letter), else 0

Heavy root letters: Those most frequently appearing in roots
Light letters: Those more commonly grammatical/structural

This is a SEMANTIC-LINGUISTIC encoding based on Arabic's trilateral root system.
"""

# Classification based on frequency analysis of Arabic roots
# "Heavy" letters appear more often in semantic roots
# "Light" letters appear more often in grammatical patterns

# Root-heavy consonants (semantic weight)
ROOT_HEAVY = {
    'ك', 'ت', 'ب',  # common root starters
    'ع', 'ل', 'م',  # very common in roots
    'ر', 'ح', 'س',  # frequent root letters
    'ف', 'ق', 'د',  # semantic carriers
    'ن', 'ج', 'خ',  # meaning-dense
    'ص', 'ض', 'ط', 'ظ',  # emphatics (meaning markers)
    'ذ', 'ث', 'غ', 'ز', 'ش',  # less common but root-significant
}

# Pattern/grammatical letters (structural weight)
PATTERN_LIGHT = {
    'ا', 'و', 'ي',  # weak letters, often pattern
    'ه', 'ة',  # pronoun/feminine markers
    'م',  # prefix (but also root-heavy, ambiguous)
    'ء', 'أ', 'إ', 'آ', 'ؤ', 'ئ',  # hamza variants
    'ى',  # alif maqsura
}

ROOT_MAP = {}
for letter in ROOT_HEAVY:
    ROOT_MAP[letter] = 1
for letter in PATTERN_LIGHT:
    ROOT_MAP[letter] = 0
# م is ambiguous - appears in both; treating as heavy
ROOT_MAP['م'] = 1


def encode_text(text: str) -> str:
    """Encode text using root-weight."""
    import re
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    clean = diacritics.sub('', text)

    bits = []
    for char in clean:
        if char in ROOT_MAP:
            bits.append(str(ROOT_MAP[char]))

    return ''.join(bits)


def get_stats() -> dict:
    heavy = sum(1 for v in ROOT_MAP.values() if v == 1)
    light = sum(1 for v in ROOT_MAP.values() if v == 0)
    return {
        "encoding": "f_root",
        "description": "1 if root-heavy letter, 0 if pattern/grammatical",
        "heavy_letters": heavy,
        "light_letters": light,
        "baseline_density": heavy / (heavy + light) if (heavy + light) > 0 else 0
    }

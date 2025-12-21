"""
f_voice: Phonetic Voicing Encoding

f_voice(letter) = 1 if voiced consonant, else 0

Voiced = vocal cords vibrate (agency, presence)
Voiceless = no vibration (absence, passivity)

This is a PHONETIC encoding, independent of visual (dot) features.
"""

# Arabic consonant voicing classification
# Based on classical Arabic phonology

VOICED = {
    # Voiced stops
    'ب', 'د', 'ض', 'ط',  # note: ط is emphatic but voiced
    # Voiced fricatives
    'ذ', 'ز', 'ظ', 'غ', 'ع',
    # Nasals (always voiced)
    'م', 'ن',
    # Liquids (always voiced)
    'ل', 'ر',
    # Glides (voiced)
    'و', 'ي',
    # Voiced pharyngeal
    'ع',
}

VOICELESS = {
    # Voiceless stops
    'ت', 'ك', 'ق', 'ء', 'ح',
    # Voiceless fricatives
    'ث', 'ف', 'س', 'ص', 'ش', 'خ', 'ه',
    # Voiceless emphatics
    'ص', 'ط',  # ط debatable, treating as voiced above
}

# Vowel carriers (neutral - treat as 0)
NEUTRAL = {'ا', 'أ', 'إ', 'آ', 'ة', 'ى', 'ئ', 'ؤ'}

VOICE_MAP = {}
for letter in VOICED:
    VOICE_MAP[letter] = 1
for letter in VOICELESS:
    VOICE_MAP[letter] = 0
for letter in NEUTRAL:
    VOICE_MAP[letter] = 0  # treating vowel carriers as "voiceless"


def encode_text(text: str) -> str:
    """Encode text using voicing."""
    import re
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    clean = diacritics.sub('', text)

    bits = []
    for char in clean:
        if char in VOICE_MAP:
            bits.append(str(VOICE_MAP[char]))

    return ''.join(bits)


def get_stats() -> dict:
    voiced = sum(1 for v in VOICE_MAP.values() if v == 1)
    voiceless = sum(1 for v in VOICE_MAP.values() if v == 0)
    return {
        "encoding": "f_voice",
        "description": "1 if voiced consonant, 0 if voiceless/vowel",
        "voiced_letters": voiced,
        "voiceless_letters": voiceless,
        "baseline_density": voiced / (voiced + voiceless) if (voiced + voiceless) > 0 else 0
    }

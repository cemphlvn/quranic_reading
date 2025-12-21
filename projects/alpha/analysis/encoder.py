#!/usr/bin/env python3
"""
Dot Encoder for H1: Dot Density Hypothesis
Encodes Arabic text to dot-bitstring and computes dot-density ratios.
"""

import json
import re
from pathlib import Path
from typing import Tuple, List, Dict

# Load dot encoding data
DATA_PATH = Path(__file__).parent.parent / "data" / "dot_encoding.json"

def load_encoding() -> Dict:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

ENCODING = load_encoding()

# Build lookup table
DOT_LOOKUP = {}
for letter, info in ENCODING['letters'].items():
    DOT_LOOKUP[letter] = info['dot_status']
for letter, info in ENCODING['variants'].items():
    DOT_LOOKUP[letter] = info['dot_status']


def extract_letters(text: str) -> str:
    """Extract only Arabic letters from text, removing diacritics and spaces."""
    # Arabic diacritics (tashkil) to remove
    diacritics = re.compile(r'[\u064B-\u0652\u0670]')  # fatha, damma, kasra, shadda, sukun, etc.
    text = diacritics.sub('', text)

    # Keep only Arabic letters
    letters = []
    for char in text:
        if char in DOT_LOOKUP:
            letters.append(char)
    return ''.join(letters)


def encode_to_bitstring(text: str) -> str:
    """
    Encode Arabic text to dot-bitstring.
    1 = letter has dots
    0 = letter has no dots
    """
    letters = extract_letters(text)
    bits = []
    for letter in letters:
        if letter in DOT_LOOKUP:
            bits.append(str(DOT_LOOKUP[letter]))
    return ''.join(bits)


def compute_dot_density(text: str) -> Tuple[float, int, int]:
    """
    Compute dot density ratio.
    Returns: (density, dotted_count, total_count)
    """
    bitstring = encode_to_bitstring(text)
    if not bitstring:
        return (0.0, 0, 0)

    dotted = bitstring.count('1')
    total = len(bitstring)
    density = dotted / total

    return (density, dotted, total)


def analyze_text(text: str, label: str = "Text") -> Dict:
    """Full analysis of a text segment."""
    letters = extract_letters(text)
    bitstring = encode_to_bitstring(text)
    density, dotted, total = compute_dot_density(text)

    # Count individual letters
    letter_freq = {}
    for letter in letters:
        letter_freq[letter] = letter_freq.get(letter, 0) + 1

    return {
        'label': label,
        'original': text,
        'letters_only': letters,
        'bitstring': bitstring,
        'total_letters': total,
        'dotted_count': dotted,
        'undotted_count': total - dotted,
        'dot_density': round(density, 4),
        'letter_frequency': letter_freq
    }


def format_analysis(result: Dict) -> str:
    """Format analysis result for display."""
    lines = [
        f"=== {result['label']} ===",
        f"Original: {result['original']}",
        f"Letters:  {result['letters_only']}",
        f"Bitstring: {result['bitstring']}",
        f"",
        f"Total letters: {result['total_letters']}",
        f"Dotted:        {result['dotted_count']}",
        f"Undotted:      {result['undotted_count']}",
        f"Dot density:   {result['dot_density']} ({result['dot_density']*100:.1f}%)",
    ]
    return '\n'.join(lines)


# === TEST ON SURAH AL-FATIHA ===

FATIHA = """
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَٰنِ الرَّحِيمِ
مَالِكِ يَوْمِ الدِّينِ
إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
"""

FATIHA_VERSES = [
    ("Basmala", "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"),
    ("Verse 2", "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"),
    ("Verse 3", "الرَّحْمَٰنِ الرَّحِيمِ"),
    ("Verse 4", "مَالِكِ يَوْمِ الدِّينِ"),
    ("Verse 5", "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ"),
    ("Verse 6", "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ"),
    ("Verse 7", "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"),
]


if __name__ == "__main__":
    print("=" * 60)
    print("H1: DOT DENSITY ENCODER")
    print("=" * 60)
    print()

    # Full Surah Analysis
    full_result = analyze_text(FATIHA, "Surah Al-Fatiha (Full)")
    print(format_analysis(full_result))
    print()

    # Verse-by-verse analysis
    print("=" * 60)
    print("VERSE-BY-VERSE ANALYSIS")
    print("=" * 60)
    print()

    print(f"{'Verse':<12} {'Letters':>7} {'Dotted':>7} {'Density':>8} {'Bitstring'}")
    print("-" * 80)

    for label, verse in FATIHA_VERSES:
        result = analyze_text(verse, label)
        print(f"{label:<12} {result['total_letters']:>7} {result['dotted_count']:>7} {result['dot_density']:>8.2%} {result['bitstring']}")

    print()
    print("=" * 60)
    print("OBSERVATIONS")
    print("=" * 60)

    densities = [analyze_text(v, l)['dot_density'] for l, v in FATIHA_VERSES]
    print(f"Min density: {min(densities):.2%}")
    print(f"Max density: {max(densities):.2%}")
    print(f"Range:       {max(densities) - min(densities):.2%}")
    print(f"Mean:        {sum(densities)/len(densities):.2%}")

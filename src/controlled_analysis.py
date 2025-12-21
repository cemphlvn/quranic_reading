"""
CONTROLLED ANALYSIS

Problem: Word boundaries create structure that dominates all encodings.
Solution: Compare each encoding with a WORD-PRESERVING null model.

Method:
1. For each word, shuffle letters WITHIN the word
2. This preserves word structure but randomizes letter order
3. Compare real encoding with word-shuffled encoding
4. Only structure BEYOND word-level remains

This is the critical test for "hidden message" vs "just language structure."
"""

import sys
import random
import re
from pathlib import Path
from collections import Counter
from typing import List, Callable

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, compression_ratio
)
from research_loop import ALL_ENCODINGS, strip_diacritics


def shuffle_within_words(text: str) -> str:
    """Shuffle letters within each word, preserving word boundaries."""
    clean = strip_diacritics(text)

    # Split into words and non-words
    tokens = re.split(r'([\u0621-\u064A]+)', clean)

    result = []
    for token in tokens:
        if re.match(r'^[\u0621-\u064A]+$', token):
            # Arabic word - shuffle it
            letters = list(token)
            random.shuffle(letters)
            result.append(''.join(letters))
        else:
            # Non-word - keep as is
            result.append(token)

    return ''.join(result)


def word_controlled_test(name: str, encode_fn: Callable, text: str, n_shuffles: int = 30):
    """Test encoding against word-preserving null model."""
    # Encode real text
    real_bits = encode_fn(text)
    if len(real_bits) < 100:
        return None

    real_comp = compression_ratio(real_bits)

    # Generate word-shuffled versions
    null_comps = []
    for _ in range(n_shuffles):
        shuffled_text = shuffle_within_words(text)
        shuffled_bits = encode_fn(shuffled_text)
        null_comps.append(compression_ratio(shuffled_bits))

    # Calculate z-score
    null_mean = sum(null_comps) / len(null_comps)
    null_std = (sum((x - null_mean)**2 for x in null_comps) / len(null_comps)) ** 0.5

    if null_std > 0:
        z_score = (real_comp - null_mean) / null_std
    else:
        z_score = 0

    return {
        'name': name,
        'real_compression': real_comp,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z_score,
        'significant': abs(z_score) > 2,
        'direction': 'more_structured' if z_score < -2 else ('less_structured' if z_score > 2 else 'same')
    }


def main():
    """Run controlled analysis."""
    print("="*80)
    print("CONTROLLED ANALYSIS: STRUCTURE BEYOND WORD BOUNDARIES")
    print("="*80)
    print()
    print("Null model: Letters shuffled WITHIN words (preserving word structure)")
    print("Test: Does encoding reveal structure BEYOND what words explain?")
    print()

    # Load data
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")
    print(f"Loaded Quran: {len(text)} characters")

    # Test each encoding
    results = []
    print("\nTesting encodings (this may take a while)...")

    for name, fn in ALL_ENCODINGS.items():
        result = word_controlled_test(name, fn, text, n_shuffles=20)
        if result:
            results.append(result)
            sig = "***" if result['significant'] else ""
            print(f"  {name}: z={result['z_score']:.2f} {sig}")

    # Sort by z-score
    results.sort(key=lambda x: x['z_score'])

    # Print report
    print("\n" + "="*80)
    print("RESULTS: ENCODING STRUCTURE BEYOND WORD BOUNDARIES")
    print("="*80)

    print("\n{:<20} {:>12} {:>12} {:>12} {:>15}".format(
        "Encoding", "Real Comp", "Null Mean", "Z-score", "Beyond Words?"
    ))
    print("-"*80)

    for r in results:
        beyond = "YES" if r['significant'] and r['direction'] == 'more_structured' else "no"
        print("{:<20} {:>12.4f} {:>12.4f} {:>12.2f} {:>15}".format(
            r['name'], r['real_compression'], r['null_mean'], r['z_score'], beyond
        ))

    # Summary
    beyond_words = [r for r in results if r['significant'] and r['direction'] == 'more_structured']

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    print(f"\nEncodings with structure BEYOND word boundaries: {len(beyond_words)}/{len(results)}")

    if beyond_words:
        print("\nThese encodings show structure that cannot be explained by word-level patterns:")
        for r in beyond_words:
            print(f"  - {r['name']}: z={r['z_score']:.2f}")

        print("\nInterpretation:")
        print("  These patterns exist in the ARRANGEMENT of specific letter types")
        print("  that goes beyond what random word-internal order would produce.")
        print("  This could indicate:")
        print("    1. Phonetic patterns (euphony, tajweed)")
        print("    2. Morphological patterns (root/pattern system)")
        print("    3. Deliberate structure (unknown cause)")
    else:
        print("\nNo encoding shows structure beyond word boundaries.")
        print("All observed structure can be explained by word-level patterns.")
        print("The 'hidden message' hypothesis is NOT supported.")

    print("\n" + "="*80)

    return results


if __name__ == "__main__":
    main()

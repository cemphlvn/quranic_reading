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


# Statistical constants
import math
N_ENCODINGS = 16
ALPHA = 0.05
ALPHA_CORRECTED = ALPHA / N_ENCODINGS  # 0.003125
Z_THRESHOLD_RAW = 1.96
Z_THRESHOLD_CORRECTED = 2.96


def z_to_p(z: float) -> float:
    """Convert z-score to two-tailed p-value."""
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def word_controlled_test(name: str, encode_fn: Callable, text: str, n_shuffles: int = 1000):
    """
    Test encoding against word-preserving null model.
    Uses 1000 iterations and Bonferroni correction.
    """
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

    p_value = z_to_p(z_score)
    sig_raw = abs(z_score) > Z_THRESHOLD_RAW
    sig_corrected = abs(z_score) > Z_THRESHOLD_CORRECTED

    return {
        'name': name,
        'real_compression': real_comp,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z_score,
        'p_value': p_value,
        'significant_raw': sig_raw,
        'significant_corrected': sig_corrected,
        'direction': 'more_structured' if z_score < -Z_THRESHOLD_CORRECTED else (
            'less_structured' if z_score > Z_THRESHOLD_CORRECTED else 'same')
    }


def main():
    """Run controlled analysis with Bonferroni correction."""
    print("="*90)
    print("CONTROLLED ANALYSIS: STRUCTURE BEYOND WORD BOUNDARIES")
    print(f"Statistical: n=1000 shuffles, Bonferroni α={ALPHA_CORRECTED:.4f}, |z|>{Z_THRESHOLD_CORRECTED}")
    print("="*90)
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
    print("\nTesting encodings (1000 shuffles each, this will take a while)...")

    for name, fn in ALL_ENCODINGS.items():
        result = word_controlled_test(name, fn, text, n_shuffles=1000)
        if result:
            results.append(result)
            if result['significant_corrected']:
                sig = "✓✓"
            elif result['significant_raw']:
                sig = "✓ "
            else:
                sig = "✗ "
            print(f"  {sig} {name}: z={result['z_score']:.2f}, p={result['p_value']:.4f}")

    # Sort by z-score
    results.sort(key=lambda x: x['z_score'])

    # Print report
    print("\n" + "="*90)
    print("RESULTS: ENCODING STRUCTURE BEYOND WORD BOUNDARIES")
    print(f"Bonferroni correction: α={ALPHA_CORRECTED:.4f}")
    print("="*90)

    print("\n{:<18} {:>10} {:>10} {:>10} {:>10} {:>22}".format(
        "Encoding", "Real Comp", "Null Mean", "Z-score", "p-value", "Beyond Words?"
    ))
    print("-"*90)

    for r in results:
        if r['significant_corrected'] and r['direction'] == 'more_structured':
            beyond = "YES (corrected)"
        elif r['significant_raw'] and r['direction'] == 'more_structured':
            beyond = "yes (uncorrected)"
        else:
            beyond = "no"
        print("{:<18} {:>10.4f} {:>10.4f} {:>10.2f} {:>10.4f} {:>22}".format(
            r['name'], r['real_compression'], r['null_mean'], r['z_score'], r['p_value'], beyond
        ))

    # Summary
    beyond_corrected = [r for r in results if r['significant_corrected'] and r['direction'] == 'more_structured']
    beyond_raw = [r for r in results if r['significant_raw'] and not r['significant_corrected'] and r['direction'] == 'more_structured']

    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)

    print(f"\nEncodings with structure BEYOND word boundaries:")
    print(f"  Bonferroni-corrected: {len(beyond_corrected)}/{len(results)}")
    print(f"  Uncorrected only: {len(beyond_raw)}/{len(results)}")

    if beyond_corrected:
        print("\nSignificant after Bonferroni correction (robust findings):")
        for r in beyond_corrected:
            print(f"  - {r['name']}: z={r['z_score']:.2f}, p={r['p_value']:.6f}")

        print("\nInterpretation:")
        print("  These patterns exist in the ARRANGEMENT of specific letter types")
        print("  that goes beyond what random word-internal order would produce.")
        print("  This could indicate:")
        print("    1. Phonetic patterns (euphony, tajweed)")
        print("    2. Morphological patterns (root/pattern system)")
        print("    3. General Arabic language properties (NOT proven Quran-specific)")
    else:
        print("\nNo encoding shows structure beyond word boundaries after correction.")
        print("All observed structure can be explained by word-level patterns.")
        print("The 'hidden message' hypothesis is NOT supported.")

    print("\n" + "="*80)

    return results


if __name__ == "__main__":
    main()

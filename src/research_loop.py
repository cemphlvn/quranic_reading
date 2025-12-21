"""
RESEARCH LOOP

Iterate through encodings and interpretations until convergence.
Add new encodings based on findings. Test hypotheses systematically.

This is the MAIN executable for the research project.
"""

import sys
import json
import random
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, shannon_entropy, compression_ratio,
    density, run_length_analysis, autocorrelation
)
from research_engine import (
    ENCODINGS, extract_letters, ABJAD, strip_diacritics,
    null_test, EncodingResult, NullTestResult
)

import re


# ============================================================
# ADDITIONAL ENCODINGS (ITERATION 2)
# ============================================================

# E9: First letter of root (approximate - uses position in word)
def encode_word_position(text: str) -> str:
    """E9: First letter of word = 1, else = 0."""
    clean = strip_diacritics(text)
    bits = []
    in_word = False
    for c in clean:
        if re.match(r'[\u0621-\u064A]', c):
            if not in_word:
                bits.append('1')  # first letter
                in_word = True
            else:
                bits.append('0')  # not first
        else:
            in_word = False
    return ''.join(bits)


# E10: Last letter of word = 1
def encode_word_end(text: str) -> str:
    """E10: Last letter of word = 1, else = 0."""
    clean = strip_diacritics(text)
    # Find word boundaries
    words = re.findall(r'[\u0621-\u064A]+', clean)
    bits = []
    for word in words:
        for i, c in enumerate(word):
            if i == len(word) - 1:
                bits.append('1')
            else:
                bits.append('0')
    return ''.join(bits)


# E11: Alphabet order parity (position in alphabet)
ALPHA_ORDER = 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
ALPHA_POS = {c: i for i, c in enumerate(ALPHA_ORDER)}

def encode_alpha_parity(text: str) -> str:
    """E11: Odd position in alphabet = 1, even = 0."""
    letters = extract_letters(text)
    return ''.join(str(ALPHA_POS.get(c, 0) % 2) for c in letters if c in ALPHA_POS)


# E12: High frequency letter = 1 (above median frequency)
def encode_high_freq(text: str) -> str:
    """E12: High frequency letter = 1, low = 0."""
    letters = extract_letters(text)
    freq = Counter(letters)
    median = sorted(freq.values())[len(freq)//2]
    high_freq = {k for k, v in freq.items() if v >= median}
    return ''.join('1' if c in high_freq else '0' for c in letters)


# E13: Letter appears in "Allah" (الله) = 1
ALLAH_LETTERS = set('اللله')
def encode_allah_letter(text: str) -> str:
    """E13: Letter in 'Allah' = 1, else = 0."""
    letters = extract_letters(text)
    return ''.join('1' if c in ALLAH_LETTERS else '0' for c in letters)


# E14: Mirrored letters (look same when flipped)
SYMMETRIC = set('اودذرزسشصض')  # approximately symmetric letters
def encode_symmetric(text: str) -> str:
    """E14: Symmetric/mirrored letter = 1, else = 0."""
    letters = extract_letters(text)
    return ''.join('1' if c in SYMMETRIC else '0' for c in letters)


# E15: Ascending letters (extend above baseline)
ASCENDING = set('اأإآلكطظ')
def encode_ascending(text: str) -> str:
    """E15: Ascending letter = 1, else = 0."""
    letters = extract_letters(text)
    return ''.join('1' if c in ASCENDING else '0' for c in letters)


# E16: Descending letters (extend below baseline)
DESCENDING = set('يئىرزنق')
def encode_descending(text: str) -> str:
    """E16: Descending letter = 1, else = 0."""
    letters = extract_letters(text)
    return ''.join('1' if c in DESCENDING else '0' for c in letters)


# Combined encoding registry
ALL_ENCODINGS = {
    **ENCODINGS,
    'E9_word_start': encode_word_position,
    'E10_word_end': encode_word_end,
    'E11_alpha_parity': encode_alpha_parity,
    'E12_high_freq': encode_high_freq,
    'E13_allah_letter': encode_allah_letter,
    'E14_symmetric': encode_symmetric,
    'E15_ascending': encode_ascending,
    'E16_descending': encode_descending,
}


# ============================================================
# RESEARCH LOOP
# ============================================================

@dataclass
class FindingSummary:
    """Summary of one encoding's findings."""
    encoding: str
    length: int
    density: float
    compression: float
    z_score: float
    significant: bool
    interpretation_notes: str


def run_encoding_test(name: str, fn, text: str, n_null: int = 30) -> FindingSummary:
    """Test one encoding thoroughly."""
    bits = fn(text)
    if len(bits) < 100:
        return None

    d = density(bits)
    c = compression_ratio(bits)
    runs = run_length_analysis(bits)

    # Null test
    null = null_test(bits, n_null)

    # Generate interpretation notes
    notes = []
    if runs['max_0_run'] > 50:
        notes.append(f"long 0-run: {runs['max_0_run']}")
    if runs['max_1_run'] > 50:
        notes.append(f"long 1-run: {runs['max_1_run']}")
    if bits.count('1') % 19 == 0:
        notes.append("1s div by 19")
    if d < 0.1:
        notes.append("sparse (low density)")
    if d > 0.9:
        notes.append("dense (high density)")

    return FindingSummary(
        encoding=name,
        length=len(bits),
        density=d,
        compression=c,
        z_score=null.z_compression,
        significant=null.significant,
        interpretation_notes="; ".join(notes) if notes else "standard"
    )


def run_research_loop(text: str, iterations: int = 1) -> List[FindingSummary]:
    """Main research loop."""
    print("="*80)
    print("RESEARCH LOOP: SYSTEMATIC ANALYSIS")
    print("="*80)
    print(f"\nEncodings to test: {len(ALL_ENCODINGS)}")
    print(f"Iterations: {iterations}")

    all_results = []

    for iteration in range(iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        results = []
        for name, fn in ALL_ENCODINGS.items():
            result = run_encoding_test(name, fn, text)
            if result:
                results.append(result)
                status = "✓" if result.significant else "✗"
                print(f"  {status} {name}: z={result.z_score:.2f}, d={result.density:.3f}")

        all_results.extend(results)

    # Sort by z-score (most significant first)
    all_results.sort(key=lambda x: x.z_score)

    return all_results


def print_final_report(results: List[FindingSummary]):
    """Print comprehensive report."""
    print("\n" + "="*80)
    print("FINAL REPORT: ALL ENCODINGS RANKED BY STRUCTURE")
    print("="*80)

    print("\n{:<20} {:>8} {:>10} {:>10} {:>12} {:>10}".format(
        "Encoding", "Length", "Density", "Compress", "Z-score", "Status"
    ))
    print("-"*80)

    for r in results:
        status = "VALID" if r.significant else "invalid"
        print("{:<20} {:>8} {:>10.4f} {:>10.4f} {:>12.2f} {:>10}".format(
            r.encoding, r.length, r.density, r.compression, r.z_score, status
        ))

    # Summary statistics
    valid = [r for r in results if r.significant]
    invalid = [r for r in results if not r.significant]

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal encodings tested: {len(results)}")
    print(f"Valid (significant structure): {len(valid)}")
    print(f"Invalid (no significant structure): {len(invalid)}")

    if valid:
        # Top 5 by structure
        print("\nTOP 5 ENCODINGS BY STRUCTURE:")
        for i, r in enumerate(valid[:5], 1):
            print(f"  {i}. {r.encoding}: z={r.z_score:.2f}")
            if r.interpretation_notes != "standard":
                print(f"     Notes: {r.interpretation_notes}")

        # Categorize by interpretation type
        print("\nFINDINGS BY CATEGORY:")

        morphological = [r for r in valid if r.encoding in ['E1_dot', 'E5_connect', 'E14_symmetric', 'E15_ascending', 'E16_descending']]
        phonetic = [r for r in valid if r.encoding in ['E2_voice', 'E3_emphasis', 'E4_throat', 'E8_solar']]
        numerical = [r for r in valid if r.encoding in ['E6_abjad_parity', 'E7_abjad_prime', 'E11_alpha_parity']]
        positional = [r for r in valid if r.encoding in ['E9_word_start', 'E10_word_end']]
        semantic = [r for r in valid if r.encoding in ['E12_high_freq', 'E13_allah_letter']]

        print(f"  Morphological: {len(morphological)}/{len(valid)}")
        print(f"  Phonetic: {len(phonetic)}/{len(valid)}")
        print(f"  Numerical: {len(numerical)}/{len(valid)}")
        print(f"  Positional: {len(positional)}/{len(valid)}")
        print(f"  Semantic: {len(semantic)}/{len(valid)}")

    # Key insight
    print("\n" + "="*80)
    print("KEY INSIGHT")
    print("="*80)

    if valid:
        best = valid[0]
        print(f"\nStrongest encoding: {best.encoding} (z = {best.z_score:.2f})")
        print(f"This encoding produces the most non-random structure.")
        print(f"The bitstring is {(1 - best.compression) * 100:.1f}% compressible,")
        print(f"meaning it contains significant predictable patterns.")
    else:
        print("\nNo encodings showed significant structure.")
        print("The null hypothesis (random pattern) cannot be rejected.")


def main():
    """Main entry point."""
    # Load data
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")
    print(f"Loaded Quran: {len(text)} characters")

    # Run research loop
    results = run_research_loop(text, iterations=1)

    # Print final report
    print_final_report(results)

    # Save results
    output = [asdict(r) for r in results]
    with open("projects/alpha/data/research_loop_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to projects/alpha/data/research_loop_results.json")

    return results


if __name__ == "__main__":
    main()

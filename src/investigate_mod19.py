"""
INVESTIGATE MOD-19 FINDING

Two encodings (E1_dot, E3_emphasis) have total 1s divisible by 19.
Is this significant or coincidence?

Null hypothesis: Random encoding would have ~5.3% chance of being divisible by 19.
If multiple encodings pass, probability drops multiplicatively.
"""

import sys
import random
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import load_quran, extract_text
from research_engine import ENCODINGS, extract_letters, ABJAD


def analyze_mod19():
    """Deep analysis of mod-19 patterns."""
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")

    print("MOD-19 ANALYSIS")
    print("="*60)

    results = []
    for name, fn in ENCODINGS.items():
        bits = fn(text)
        total_1s = bits.count('1')
        total_0s = bits.count('0')
        mod_1s = total_1s % 19
        mod_0s = total_0s % 19
        mod_len = len(bits) % 19

        results.append({
            'name': name,
            'length': len(bits),
            'total_1s': total_1s,
            'total_0s': total_0s,
            'mod19_1s': mod_1s,
            'mod19_0s': mod_0s,
            'mod19_len': mod_len,
            'divisible_1s': mod_1s == 0,
            'divisible_0s': mod_0s == 0,
        })

    print("\n{:<20} {:>10} {:>10} {:>8} {:>8} {:>8}".format(
        "Encoding", "Total 1s", "Total 0s", "mod19(1)", "mod19(0)", "mod19(L)"
    ))
    print("-"*60)

    for r in results:
        mark_1 = "***" if r['divisible_1s'] else ""
        mark_0 = "***" if r['divisible_0s'] else ""
        print("{:<20} {:>10} {:>10} {:>8}{} {:>5}{}  {:>8}".format(
            r['name'], r['total_1s'], r['total_0s'],
            r['mod19_1s'], mark_1, r['mod19_0s'], mark_0, r['mod19_len']
        ))

    # Count how many are divisible by 19
    div_1s = sum(1 for r in results if r['divisible_1s'])
    div_0s = sum(1 for r in results if r['divisible_0s'])

    print("\n" + "="*60)
    print(f"Encodings with 1s divisible by 19: {div_1s}/{len(results)}")
    print(f"Encodings with 0s divisible by 19: {div_0s}/{len(results)}")

    # Probability calculation
    p_one = 1/19  # probability one encoding is divisible by 19
    n_encodings = len(results)

    # Expected number divisible
    expected = n_encodings * p_one
    print(f"\nExpected by chance: {expected:.2f}")

    # Binomial probability of getting k or more
    from math import comb
    def binom_prob(n, k, p):
        """P(X >= k) for binomial(n, p)"""
        return sum(comb(n, i) * (p**i) * ((1-p)**(n-i)) for i in range(k, n+1))

    p_1s = binom_prob(n_encodings, div_1s, p_one)
    p_0s = binom_prob(n_encodings, div_0s, p_one)

    print(f"P(≥{div_1s} divisible | random): {p_1s:.4f}")
    print(f"P(≥{div_0s} divisible | random): {p_0s:.4f}")

    if p_1s < 0.05:
        print("\n>>> 1s divisibility is STATISTICALLY SIGNIFICANT")
    else:
        print("\n>>> 1s divisibility is NOT significant (could be chance)")

    # Check total across all encodings
    print("\n" + "="*60)
    print("CROSS-ENCODING ANALYSIS")
    print("="*60)

    # Total letter count
    letters = extract_letters(text)
    print(f"\nTotal letters in Quran: {len(letters)}")
    print(f"mod 19: {len(letters) % 19}")

    # Letter frequency analysis
    freq = Counter(letters)
    print(f"\nLetter frequencies (top 10):")
    for letter, count in freq.most_common(10):
        abjad_val = ABJAD.get(letter, 0)
        print(f"  {letter}: {count} (abjad={abjad_val}, mod19={count % 19})")

    # Check if specific letters have counts divisible by 19
    print("\nLetters with count divisible by 19:")
    for letter, count in freq.items():
        if count % 19 == 0:
            print(f"  {letter}: {count} = 19 × {count // 19}")

    # Abjad sum
    total_abjad = sum(ABJAD.get(l, 0) for l in letters)
    print(f"\nTotal Abjad value: {total_abjad}")
    print(f"mod 19: {total_abjad % 19}")
    print(f"mod 114: {total_abjad % 114}")  # 114 = 6 × 19

    return results


if __name__ == "__main__":
    analyze_mod19()

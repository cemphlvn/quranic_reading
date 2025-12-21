"""
FALSIFICATION TEST

Scientific method: Try to DISPROVE each hypothesis.
If we cannot disprove it, it gains credibility.

THREE ENCODINGS TESTED:
1. f_dot   - morphological (visual dots)
2. f_voice - phonetic (vocal cord vibration)
3. f_root  - semantic (root vs pattern letters)

FALSIFICATION ATTEMPTS:
1. Compare with shuffled text (null model)
2. Compare with random encoding (control)
3. Check if structure is just letter frequency artifact
4. Cross-validate between encodings
"""

import sys
import random
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, analyze_bitstring,
    compare_with_null, shannon_entropy, compression_ratio,
    density, run_length_analysis
)
from encoding_functions.f_dot import encode_text as f_dot
from encoding_functions.f_voice import encode_text as f_voice
from encoding_functions.f_root import encode_text as f_root


def random_encoding(text: str) -> str:
    """Control: random 0/1 assignment per letter."""
    import re
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    arabic = re.compile(r'[\u0621-\u064A]')
    clean = diacritics.sub('', text)
    return ''.join(str(random.randint(0, 1)) for c in clean if arabic.match(c))


def run_test(name: str, encode_fn, text: str, n_null: int = 30):
    """Run encoding test with falsification attempts."""
    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print('='*60)

    # Encode
    bitstring = encode_fn(text)
    if not bitstring:
        print("  ERROR: Empty bitstring")
        return None

    # Basic stats
    print(f"\n[1] BASIC STATISTICS")
    print(f"  Length: {len(bitstring)}")
    print(f"  Density (1s): {density(bitstring):.4f}")
    print(f"  Entropy: {shannon_entropy(bitstring):.4f}")
    print(f"  Compression: {compression_ratio(bitstring):.4f}")

    runs = run_length_analysis(bitstring)
    print(f"  Max 0-run: {runs['max_0_run']}")
    print(f"  Max 1-run: {runs['max_1_run']}")
    print(f"  Total runs: {runs['total_runs']}")

    # FALSIFICATION 1: Null model comparison
    print(f"\n[2] FALSIFICATION: NULL MODEL (shuffled text)")

    null_compressions = []
    null_entropies = []
    bits_list = list(bitstring)

    for _ in range(n_null):
        random.shuffle(bits_list)
        shuffled = ''.join(bits_list)
        null_compressions.append(compression_ratio(shuffled))
        null_entropies.append(shannon_entropy(shuffled))

    real_comp = compression_ratio(bitstring)
    null_mean_comp = sum(null_compressions) / len(null_compressions)
    null_std_comp = (sum((x - null_mean_comp)**2 for x in null_compressions) / len(null_compressions)) ** 0.5

    if null_std_comp > 0:
        z_comp = (real_comp - null_mean_comp) / null_std_comp
    else:
        z_comp = 0

    print(f"  Real compression: {real_comp:.4f}")
    print(f"  Null mean: {null_mean_comp:.4f} (std: {null_std_comp:.4f})")
    print(f"  Z-score: {z_comp:.2f}")

    if abs(z_comp) > 2:
        print(f"  >>> FALSIFICATION FAILED: Structure differs from random (p<0.05)")
        null_falsified = False
    else:
        print(f"  >>> FALSIFICATION SUCCEEDED: No significant structure")
        null_falsified = True

    # FALSIFICATION 2: Is it just letter frequency?
    print(f"\n[3] FALSIFICATION: LETTER FREQUENCY ARTIFACT")

    # If the pattern is just from uneven letter distribution,
    # then long runs should match expected from density
    d = density(bitstring)
    expected_avg_0_run = 1 / (1 - (1-d)) if d < 1 else float('inf')
    expected_avg_1_run = 1 / d if d > 0 else float('inf')
    actual_avg_0 = runs['avg_0_run']
    actual_avg_1 = runs['avg_1_run']

    print(f"  Density: {d:.4f}")
    print(f"  Expected avg 0-run (if random): ~{1/(d+0.001):.2f}")
    print(f"  Actual avg 0-run: {actual_avg_0:.2f}")
    print(f"  Expected avg 1-run (if random): ~{1/(1-d+0.001):.2f}")
    print(f"  Actual avg 1-run: {actual_avg_1:.2f}")

    # FALSIFICATION 3: Random encoding control
    print(f"\n[4] CONTROL: RANDOM ENCODING")
    random_bits = random_encoding(text)
    random_comp = compression_ratio(random_bits)
    print(f"  Random encoding compression: {random_comp:.4f}")
    print(f"  Real encoding compression: {real_comp:.4f}")

    if real_comp < random_comp * 0.9:
        print(f"  >>> Real encoding is MORE structured than random")
    else:
        print(f"  >>> Real encoding is similar to random")

    # Summary
    result = {
        "encoding": name,
        "length": len(bitstring),
        "density": density(bitstring),
        "compression": real_comp,
        "z_score_vs_null": z_comp,
        "null_falsified": null_falsified,
        "max_0_run": runs['max_0_run'],
        "max_1_run": runs['max_1_run'],
        "sample": bitstring[:50]
    }

    return result


def main():
    print("FALSIFICATION TEST: 3 ENCODING METHODOLOGIES")
    print("="*60)
    print("Axiom: Every finding must survive falsification attempts.")
    print("Method: Compare real encoding with null models and controls.")
    print()

    # Load data
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")
    print(f"Data: Full Quran, {len(text)} characters")

    # Run tests
    results = []

    # 1. Morphological (dots)
    r1 = run_test("f_dot (morphological/visual)", f_dot, text)
    results.append(r1)

    # 2. Phonetic (voicing)
    r2 = run_test("f_voice (phonetic/articulatory)", f_voice, text)
    results.append(r2)

    # 3. Semantic (root weight)
    r3 = run_test("f_root (semantic/linguistic)", f_root, text)
    results.append(r3)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY: FALSIFICATION RESULTS")
    print("="*60)

    print("\n{:<30} {:>12} {:>12} {:>15}".format(
        "Encoding", "Compression", "Z-score", "Structure?"
    ))
    print("-"*70)

    for r in results:
        if r:
            struct = "YES***" if not r['null_falsified'] else "no"
            print("{:<30} {:>12.4f} {:>12.2f} {:>15}".format(
                r['encoding'][:30], r['compression'], r['z_score_vs_null'], struct
            ))

    print("\n" + "-"*70)
    print("INTERPRETATION:")
    print("-"*70)

    structured = [r for r in results if r and not r['null_falsified']]
    if structured:
        print(f"\n{len(structured)}/3 encodings show NON-RANDOM structure.")
        print("These patterns in the Quran differ from shuffled text.")
        print("\nThis could mean:")
        print("  1. Linguistic structure (Arabic grammar)")
        print("  2. Deliberate pattern (authorial intent)")
        print("  3. Emergent property (unknown cause)")
        print("\nNext step: Investigate WHAT the patterns encode.")
    else:
        print("\n0/3 encodings show significant structure.")
        print("The null hypothesis holds: patterns appear random.")

    print("\n" + "="*60)

    return results


if __name__ == "__main__":
    main()

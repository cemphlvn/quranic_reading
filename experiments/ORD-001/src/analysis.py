"""
ORDINAL ENCODING EXPERIMENT

Tests letter-order encodings against word_perm null.

PRE-REGISTERED HYPOTHESES:
1. ord_parity_*: NEGATIVE CONTROL - expect NO structure beyond word-level
2. ord_high_low_*: NEGATIVE CONTROL - expect NO structure beyond word-level
3. ord_5bit_*: Tests if full ordinal information has cross-word structure
4. ord_delta_sign: Tests if letter transitions have cross-word patterns

CRITICAL NULL: word_perm
- Keeps words intact, shuffles order
- If encoding beats this → cross-word structure exists
- If not → structure is word-level only (expected for arbitrary encodings)

NOT GEMATRIA:
- We're NOT summing values to find "meaningful" totals
- We're testing COMPRESSION of sequences
- We use proper null models
- We pre-register hypotheses
- We report ALL results honestly
"""

import sys
import json
sys.path.insert(0, 'src')

from core.api import (
    register_encoding, register_corpus, quick_test,
    run_robustness_test, CORPORA
)
from encoding_functions.f_ordinal import (
    encode_ordinal_parity_abjad,
    encode_ordinal_parity_hijai,
    encode_ordinal_high_low_abjad,
    encode_ordinal_high_low_hijai,
    encode_ordinal_5bit_abjad,
    encode_ordinal_5bit_hijai,
    encode_ordinal_delta_sign,
)


def load_quran():
    """Load Quran corpus."""
    with open('data/quran/quran.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract all text
    all_text = []
    for surah in data:
        for verse in surah['verses']:
            all_text.append(verse['text'])

    text = ' '.join(all_text)
    return register_corpus(
        name="quran",
        text=text,
        source="Tanzil.net Uthmani",
        language="Arabic"
    )


def register_ordinal_encodings():
    """Register all ordinal encodings with pre-registered hypotheses."""

    # NEGATIVE CONTROLS (expect NO cross-word structure)
    register_encoding(
        name="ord_parity_abjad",
        fn=encode_ordinal_parity_abjad,
        description="Even(1)/Odd(0) position in Abjadi alphabet",
        hypothesis="NEGATIVE CONTROL: Arbitrary parity has no cross-word structure",
        preregistered=True
    )

    register_encoding(
        name="ord_parity_hijai",
        fn=encode_ordinal_parity_hijai,
        description="Even(1)/Odd(0) position in Hijā'ī alphabet",
        hypothesis="NEGATIVE CONTROL: Different order, same null expectation",
        preregistered=True
    )

    register_encoding(
        name="ord_high_low_abjad",
        fn=encode_ordinal_high_low_abjad,
        description="First half(0)/Second half(1) by Abjadi position",
        hypothesis="NEGATIVE CONTROL: Arbitrary split has no cross-word structure",
        preregistered=True
    )

    register_encoding(
        name="ord_high_low_hijai",
        fn=encode_ordinal_high_low_hijai,
        description="First half(0)/Second half(1) by Hijā'ī position",
        hypothesis="NEGATIVE CONTROL: Different order, same null expectation",
        preregistered=True
    )

    # EXPLORATORY (uncertain if cross-word structure exists)
    register_encoding(
        name="ord_5bit_abjad",
        fn=encode_ordinal_5bit_abjad,
        description="5-bit binary ordinal (Abjadi order)",
        hypothesis="EXPLORATORY: Does full ordinal info compress across words?",
        preregistered=True
    )

    register_encoding(
        name="ord_5bit_hijai",
        fn=encode_ordinal_5bit_hijai,
        description="5-bit binary ordinal (Hijā'ī order)",
        hypothesis="EXPLORATORY: Does ordering system affect compression?",
        preregistered=True
    )

    register_encoding(
        name="ord_delta_sign",
        fn=encode_ordinal_delta_sign,
        description="Sign of ordinal change: rising(1) vs falling(0)",
        hypothesis="EXPLORATORY: Do letter transitions have cross-word patterns?",
        preregistered=True
    )


def run_experiment(n_perm=1000):
    """Run the ordinal encoding experiment."""

    print("=" * 70)
    print("ORDINAL ENCODING EXPERIMENT")
    print("=" * 70)
    print()
    print("PRE-REGISTERED HYPOTHESES:")
    print("- ord_parity_*, ord_high_low_*: NEGATIVE CONTROLS (expect failure)")
    print("- ord_5bit_*, ord_delta_sign: EXPLORATORY (unknown)")
    print()
    print(f"CRITICAL NULL: word_perm (n={n_perm})")
    print("=" * 70)
    print()

    # Load data
    print("Loading Quran corpus...")
    if "quran" not in CORPORA:
        load_quran()
    print(f"Corpus loaded: {len(CORPORA['quran'].text)} characters")
    print()

    # Register encodings
    print("Registering ordinal encodings...")
    register_ordinal_encodings()
    print("Done.")
    print()

    # Test each encoding
    encodings_to_test = [
        # Negative controls
        "ord_parity_abjad",
        "ord_parity_hijai",
        "ord_high_low_abjad",
        "ord_high_low_hijai",
        # Exploratory
        "ord_5bit_abjad",
        "ord_5bit_hijai",
        "ord_delta_sign",
    ]

    results = {}

    for enc_name in encodings_to_test:
        print(f"\n{'='*60}")
        print(f"Testing: {enc_name}")
        print(f"{'='*60}")

        result = quick_test("quran", enc_name, n_perm=n_perm)
        results[enc_name] = result

        print(f"  Robust: {result['robust']}")
        for metric, r in result['results'].items():
            sig = "***" if r['significant'] else ""
            print(f"  {metric}: p={r['p_value']:.4f}, effect={r['effect_bits_per_char']:.4f} {sig}")
        print(f"  → {result['interpretation']}")

    # Summary
    print("\n")
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    negative_controls = ["ord_parity_abjad", "ord_parity_hijai",
                        "ord_high_low_abjad", "ord_high_low_hijai"]
    exploratory = ["ord_5bit_abjad", "ord_5bit_hijai", "ord_delta_sign"]

    print("\nNEGATIVE CONTROLS (should NOT beat word_perm):")
    for enc in negative_controls:
        status = "PASS (no structure)" if not results[enc]['robust'] else "UNEXPECTED"
        print(f"  {enc}: {status}")

    print("\nEXPLORATORY (unknown):")
    for enc in exploratory:
        if results[enc]['robust']:
            # Get average effect size
            avg_effect = sum(r['effect_bits_per_char']
                           for r in results[enc]['results'].values()) / 3
            status = f"STRUCTURE FOUND (avg effect: {avg_effect:.4f} bits/char)"
        else:
            status = "No cross-word structure"
        print(f"  {enc}: {status}")

    # Honest assessment
    print("\n")
    print("=" * 70)
    print("HONEST ASSESSMENT")
    print("=" * 70)

    any_robust = any(r['robust'] for r in results.values())

    if any_robust:
        print("""
FINDING: Some ordinal encodings show cross-word structure.

INTERPRETATION CAUTION:
- This is compression structure, NOT semantic meaning
- Could be:
  * Arabic phonotactics (letter sequences)
  * Morphological constraints (root patterns)
  * Rhyme/rhythm patterns in Quran
  * Statistical artifact (check effect sizes!)

NEXT STEPS:
- Compare to other Arabic texts (cross-corpus)
- Check effect sizes (are they meaningful?)
- Run length-scale diagnostic (local or global?)

NOT EVIDENCE FOR:
- Hidden numerical codes
- Divine design
- Gematria validity
""")
    else:
        print("""
FINDING: No ordinal encoding beats word_perm robustly.

INTERPRETATION:
- Ordinal position is ARBITRARY
- Letter order in alphabet is CONVENTIONAL, not structural
- This is expected and validates our negative controls

THIS CONFIRMS:
- Methodology works (negative controls behave as expected)
- Ordinal/gematria approaches find WORD-LEVEL structure only
- No evidence for cross-word patterns in letter ordinals
""")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_perm", type=int, default=1000,
                       help="Number of permutations")
    args = parser.parse_args()

    run_experiment(n_perm=args.n_perm)

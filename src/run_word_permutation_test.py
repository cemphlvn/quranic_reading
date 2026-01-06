#!/usr/bin/env python3
"""
WORD PERMUTATION TEST

Question: Does word ORDER affect encoding compressibility?

Null model: Keep words intact, shuffle word order
- Preserves: within-word structure, word frequencies
- Destroys: word order, cross-word patterns

If original beats null → cross-word structure exists
"""

import json
import random
import zlib
from datetime import datetime
from pathlib import Path
import re

# ============================================================
# ENCODINGS
# ============================================================

ARABIC = re.compile(r'[\u0621-\u064A]')
DIACRITICS = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')

def extract(text):
    return ''.join(ARABIC.findall(DIACRITICS.sub('', text)))

DOTTED = set('بتثجخذزشضظغفقنيء')
UNDOTTED = set('احدرسصطعكلمهوى')
SOLAR = set('تثدذرزسشصضطظلن')
LUNAR = set('ابجحخعغفقكمهوي')
VOICED = set('بدذرزضظعغلمنوي')
UNVOICED = set('تثحخسشصطفقكهء')

def enc_dotted(text):
    return ''.join('1' if c in DOTTED else '0' for c in extract(text) if c in DOTTED or c in UNDOTTED)

def enc_solar(text):
    return ''.join('1' if c in SOLAR else '0' for c in extract(text) if c in SOLAR or c in LUNAR)

def enc_voiced(text):
    return ''.join('1' if c in VOICED else '0' for c in extract(text) if c in VOICED or c in UNVOICED)

ENCODINGS = [
    ('dotted', enc_dotted, 'Dotted(1) vs Undotted(0)'),
    ('solar', enc_solar, 'Solar(1) vs Lunar(0)'),
    ('voiced', enc_voiced, 'Voiced(1) vs Unvoiced(0)'),
]

# ============================================================
# COMPRESSION
# ============================================================

def compress_zlib(bits):
    return len(zlib.compress(bits.encode(), 9)) / len(bits)

def compress_bz2(bits):
    import bz2
    return len(bz2.compress(bits.encode(), 9)) / len(bits)

def compress_lzma(bits):
    import lzma
    return len(lzma.compress(bits.encode())) / len(bits)

COMPRESSORS = [
    ('zlib', compress_zlib),
    ('bz2', compress_bz2),
    ('lzma', compress_lzma),
]

# ============================================================
# WORD PERMUTATION NULL
# ============================================================

def word_permute(text, rng):
    """Shuffle word order, keep words intact."""
    words = text.split()
    rng.shuffle(words)
    return ' '.join(words)

# ============================================================
# PERMUTATION TEST
# ============================================================

def permutation_test(text, encode_fn, compress_fn, n_perm=1000, seed=42):
    """
    Test if original text's encoding compresses better than word-permuted.

    Returns:
        observed: compression ratio of original
        null_mean: mean compression ratio of permuted
        p_value: (count where null <= observed + 1) / (n_perm + 1)
        effect: null_mean - observed (positive = original more structured)
    """
    rng = random.Random(seed)

    # Original
    original_bits = encode_fn(text)
    observed = compress_fn(original_bits)

    # Null distribution
    null_ratios = []
    count_as_extreme = 0

    for _ in range(n_perm):
        perm_text = word_permute(text, rng)
        perm_bits = encode_fn(perm_text)
        null_cr = compress_fn(perm_bits)
        null_ratios.append(null_cr)

        # Count how many nulls compress as well or better
        if null_cr <= observed:
            count_as_extreme += 1

    null_mean = sum(null_ratios) / len(null_ratios)
    null_std = (sum((x - null_mean)**2 for x in null_ratios) / len(null_ratios)) ** 0.5

    # Permutation p-value
    p_value = (count_as_extreme + 1) / (n_perm + 1)

    # Effect size in bits/char
    effect = (null_mean - observed) * 8  # Convert ratio diff to bits

    return {
        'observed': observed,
        'null_mean': null_mean,
        'null_std': null_std,
        'p_value': p_value,
        'effect_bits_per_char': effect,
        'n_perm': n_perm
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("WORD PERMUTATION TEST")
    print("=" * 70)
    print()
    print("Question: Does word ORDER affect encoding compressibility?")
    print()
    print("Null: Keep words intact, shuffle word order")
    print("If p < 0.05 → word order matters for this encoding")
    print()

    # Load Quran
    print("Loading Quran...")
    with open("data/quran/quran.json") as f:
        quran = json.load(f)
    text = " ".join(v["text"] for s in quran for v in s["verses"])
    words = text.split()
    print(f"  Text: {len(text):,} chars, {len(words):,} words")
    print()

    N_PERM = 500  # Permutations per test
    print(f"Running {N_PERM} permutations per test...")
    print()

    results = []

    for enc_name, enc_fn, enc_desc in ENCODINGS:
        print(f"ENCODING: {enc_name} ({enc_desc})")
        print("-" * 60)
        print(f"{'Compressor':<12} {'Observed':>10} {'Null Mean':>10} {'Effect':>12} {'p-value':>10} {'Verdict'}")
        print("-" * 60)

        enc_results = {'encoding': enc_name, 'description': enc_desc, 'tests': {}}
        sig_count = 0

        for comp_name, comp_fn in COMPRESSORS:
            r = permutation_test(text, enc_fn, comp_fn, n_perm=N_PERM)

            if r['p_value'] < 0.05:
                verdict = "SIG *"
                sig_count += 1
            else:
                verdict = "ns"

            print(f"{comp_name:<12} {r['observed']:>10.4f} {r['null_mean']:>10.4f} "
                  f"{r['effect_bits_per_char']:>10.4f}b/c {r['p_value']:>10.4f} {verdict}")

            enc_results['tests'][comp_name] = r

        enc_results['sig_count'] = sig_count
        results.append(enc_results)

        print("-" * 60)
        if sig_count == 3:
            print("VERDICT: ROBUST - Word order matters for ALL compressors")
        elif sig_count > 0:
            print(f"VERDICT: PARTIAL - Significant for {sig_count}/3 compressors")
        else:
            print("VERDICT: NO EFFECT - Word order doesn't affect this encoding")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY: DOES WORD ORDER MATTER?")
    print("=" * 70)
    print()
    print(f"{'Encoding':<15} {'Sig Compressors':>20} {'Verdict'}")
    print("-" * 50)
    for r in results:
        if r['sig_count'] == 3:
            v = "CROSS-WORD STRUCTURE"
        elif r['sig_count'] > 0:
            v = "WEAK EVIDENCE"
        else:
            v = "NO CROSS-WORD"
        print(f"{r['encoding']:<15} {r['sig_count']:>20}/3 {v}")
    print("-" * 50)
    print()

    # Interpretation
    print("Interpretation:")
    print("  CROSS-WORD STRUCTURE = Word order affects encoding patterns")
    print("  WEAK EVIDENCE = Compressor-dependent, needs investigation")
    print("  NO CROSS-WORD = Structure is within-word only")
    print()

    # Effect size interpretation
    print("Effect size guide (bits/char):")
    print("  < 0.001 = Trivial")
    print("  0.001-0.01 = Small")
    print("  0.01-0.1 = Moderate")
    print("  > 0.1 = Large")
    print()

    # Save
    Path("output/data").mkdir(parents=True, exist_ok=True)
    with open("output/data/word_perm_results.json", "w") as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'null_model': 'word_permutation',
            'n_perm': N_PERM,
            'n_words': len(words),
            'results': results
        }, f, indent=2)
    print("Results saved to: output/data/word_perm_results.json")

if __name__ == "__main__":
    main()

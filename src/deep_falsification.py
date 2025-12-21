"""
DEEP FALSIFICATION

Question: Is the structure we found UNIQUE to the Quran,
or is it just a property of Arabic language?

Test: Generate pseudo-Arabic text with same letter frequencies.
If it shows same structure, finding is just linguistic artifact.
"""

import sys
import random
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, compression_ratio, density, run_length_analysis
)
from encoding_functions.f_dot import encode_text as f_dot
from encoding_functions.f_voice import encode_text as f_voice
from encoding_functions.f_root import encode_text as f_root
import re


def get_letter_frequencies(text: str) -> dict:
    """Get frequency distribution of Arabic letters."""
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    arabic = re.compile(r'[\u0621-\u064A]')
    clean = diacritics.sub('', text)
    letters = [c for c in clean if arabic.match(c)]
    total = len(letters)
    freq = Counter(letters)
    return {k: v/total for k, v in freq.items()}


def generate_pseudo_arabic(frequencies: dict, length: int) -> str:
    """Generate random text with same letter frequencies."""
    letters = list(frequencies.keys())
    weights = [frequencies[l] for l in letters]
    return ''.join(random.choices(letters, weights=weights, k=length))


def main():
    print("DEEP FALSIFICATION TEST")
    print("="*60)
    print()
    print("NULL HYPOTHESIS (H_null):")
    print("  The binary structure is a property of Arabic letter")
    print("  frequencies, not unique to the Quran.")
    print()
    print("If pseudo-Arabic shows same structure → H_null ACCEPTED")
    print("If Quran shows MORE structure → H_null REJECTED")
    print("="*60)

    # Load Quran
    quran = load_quran("data/quran/quran.json")
    quran_text = extract_text(quran, "full")

    # Get letter frequencies
    freqs = get_letter_frequencies(quran_text)
    print(f"\nExtracted letter frequencies from Quran")
    print(f"Unique letters: {len(freqs)}")

    # Count letters in Quran
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    arabic = re.compile(r'[\u0621-\u064A]')
    clean = diacritics.sub('', quran_text)
    quran_letters = [c for c in clean if arabic.match(c)]
    n_letters = len(quran_letters)
    print(f"Total letters: {n_letters}")

    # Generate pseudo-Arabic with same frequencies
    print("\nGenerating pseudo-Arabic text with same letter frequencies...")
    pseudo_text = generate_pseudo_arabic(freqs, n_letters)

    # Test each encoding
    encodings = [
        ("f_dot", f_dot),
        ("f_voice", f_voice),
        ("f_root", f_root),
    ]

    print("\n" + "="*60)
    print("COMPARISON: QURAN vs PSEUDO-ARABIC (same letter frequencies)")
    print("="*60)

    print("\n{:<15} {:>12} {:>12} {:>12} {:>12}".format(
        "Encoding", "Q_compress", "P_compress", "Q_max0run", "P_max0run"
    ))
    print("-"*65)

    results = []
    for name, encode_fn in encodings:
        # Encode Quran
        q_bits = encode_fn(quran_text)
        q_comp = compression_ratio(q_bits)
        q_runs = run_length_analysis(q_bits)

        # Encode pseudo-Arabic
        p_bits = encode_fn(pseudo_text)
        p_comp = compression_ratio(p_bits)
        p_runs = run_length_analysis(p_bits)

        print("{:<15} {:>12.4f} {:>12.4f} {:>12} {:>12}".format(
            name, q_comp, p_comp, q_runs['max_0_run'], p_runs['max_0_run']
        ))

        results.append({
            "encoding": name,
            "quran_compression": q_comp,
            "pseudo_compression": p_comp,
            "quran_max_0": q_runs['max_0_run'],
            "pseudo_max_0": p_runs['max_0_run'],
            "quran_max_1": q_runs['max_1_run'],
            "pseudo_max_1": p_runs['max_1_run'],
        })

    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)

    # Analyze
    quran_better = 0
    pseudo_better = 0
    for r in results:
        if r['quran_compression'] < r['pseudo_compression'] * 0.99:
            quran_better += 1
        elif r['pseudo_compression'] < r['quran_compression'] * 0.99:
            pseudo_better += 1

    print(f"\nCompression comparison (lower = more structured):")
    print(f"  Quran more structured: {quran_better}/3")
    print(f"  Pseudo-Arabic more structured: {pseudo_better}/3")

    if quran_better > pseudo_better:
        print("\n>>> H_null REJECTED")
        print("    The Quran shows MORE structure than pseudo-Arabic")
        print("    with same letter frequencies.")
        print("    The structure is NOT just a frequency artifact.")
    elif pseudo_better > quran_better:
        print("\n>>> H_null ACCEPTED")
        print("    Pseudo-Arabic shows similar or more structure.")
        print("    The finding is likely a frequency artifact.")
    else:
        print("\n>>> INCONCLUSIVE")
        print("    Similar structure in both. Need finer tests.")

    # Additional: look at max runs (word boundaries create runs)
    print("\n" + "-"*60)
    print("RUN LENGTH ANALYSIS (word structure creates long runs)")
    print("-"*60)

    for r in results:
        print(f"\n{r['encoding']}:")
        print(f"  Quran max 0-run: {r['quran_max_0']}, max 1-run: {r['quran_max_1']}")
        print(f"  Pseudo max 0-run: {r['pseudo_max_0']}, max 1-run: {r['pseudo_max_1']}")

        if r['quran_max_0'] > r['pseudo_max_0'] * 1.5 or r['quran_max_1'] > r['pseudo_max_1'] * 1.5:
            print(f"  >>> Quran has significantly longer runs")
        else:
            print(f"  >>> Similar run lengths")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()

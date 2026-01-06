"""
HYPOTHESIS TESTING ENGINE

Proper scientific testing of encoding hypotheses.
Uses multiple null models, multiple compressors, permutation p-values.

Usage:
    python3 src/hypothesis_test.py --encoding E8_solar --nulls all --perms 1000
"""

import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import load_quran, extract_text
from core.null_models import NULL_MODELS, null_word_permutation, get_transition_matrix
from core.statistics import (
    permutation_test, test_compressor_robustness,
    is_robust_across_compressors, bonferroni_threshold,
    COMPRESSORS, PermutationResult
)
from research_loop import ALL_ENCODINGS


@dataclass
class HypothesisResult:
    """Complete result of hypothesis test."""
    encoding: str
    timestamp: str

    # Observed statistics
    bitstring_length: int
    density: float
    transition_matrix: Dict[str, float]

    # Results per null model
    null_results: Dict[str, Dict[str, Any]]  # null_model -> compressor -> result

    # Summary
    significant_any: bool  # Significant under any null/compressor
    significant_all_compressors: bool  # Robust across compressors
    significant_markov: bool  # Beats Markov surrogate
    effect_size_bits_per_char: float  # Average effect size


def test_encoding(
    encoding_name: str,
    text: str,
    null_models: List[str] = None,
    n_perms: int = 1000,
    include_word_perm: bool = True
) -> HypothesisResult:
    """
    Complete hypothesis test for one encoding.

    Tests against multiple null models and compressors.
    """
    if null_models is None:
        null_models = ['random', 'markov', 'block_20']

    encode_fn = ALL_ENCODINGS[encoding_name]
    bits = encode_fn(text)

    print(f"\nTesting {encoding_name}")
    print(f"  Bitstring length: {len(bits)}")
    print(f"  Density (1-rate): {bits.count('1') / len(bits):.4f}")

    # Get transition matrix
    trans = get_transition_matrix(bits)
    print(f"  Transitions: 0→1={trans['0->1']:.3f}, 1→0={trans['1->0']:.3f}")

    all_results = {}

    # Test each null model
    for null_name in null_models:
        print(f"\n  Null model: {null_name}")
        null_fn = NULL_MODELS[null_name]

        # Test with all compressors
        compressor_results = test_compressor_robustness(
            bits, null_fn, n_perms, null_name
        )

        all_results[null_name] = {}
        for comp_name, result in compressor_results.items():
            all_results[null_name][comp_name] = asdict(result)
            sig = "***" if result.p_value < 0.05 else ""
            print(f"    {comp_name}: p={result.p_value:.4f}, Δ={result.effect_bits_per_char:.4f} bits/char {sig}")

    # Word permutation test (separate because it needs encode_fn)
    if include_word_perm:
        print(f"\n  Null model: word_permutation")
        all_results['word_permutation'] = {}

        for comp_name in COMPRESSORS:
            # Custom null for word permutation
            observed_cr = __import__('core.statistics', fromlist=['compression_ratio']).compression_ratio(bits, comp_name)

            null_crs = []
            count_extreme = 0
            for _ in range(n_perms):
                null_bits = null_word_permutation(text, encode_fn)
                null_cr = __import__('core.statistics', fromlist=['compression_ratio']).compression_ratio(null_bits, comp_name)
                null_crs.append(null_cr)
                if null_cr <= observed_cr:
                    count_extreme += 1

            p_val = (count_extreme + 1) / (n_perms + 1)
            null_mean = sum(null_crs) / len(null_crs)
            effect = (null_mean - observed_cr) * 8

            all_results['word_permutation'][comp_name] = {
                'observed': observed_cr,
                'null_mean': null_mean,
                'p_value': p_val,
                'effect_bits_per_char': effect,
                'null_model': 'word_permutation',
                'compressor': comp_name
            }
            sig = "***" if p_val < 0.05 else ""
            print(f"    {comp_name}: p={p_val:.4f}, Δ={effect:.4f} bits/char {sig}")

    # Compute summary statistics
    any_sig = False
    all_comp_sig = True
    markov_sig = False
    total_effect = 0
    effect_count = 0

    for null_name, comp_results in all_results.items():
        for comp_name, result in comp_results.items():
            if result['p_value'] < 0.05:
                any_sig = True
            else:
                all_comp_sig = False

            if null_name == 'markov' and result['p_value'] < 0.05:
                markov_sig = True

            total_effect += result['effect_bits_per_char']
            effect_count += 1

    avg_effect = total_effect / effect_count if effect_count > 0 else 0

    return HypothesisResult(
        encoding=encoding_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
        bitstring_length=len(bits),
        density=bits.count('1') / len(bits),
        transition_matrix=trans,
        null_results=all_results,
        significant_any=any_sig,
        significant_all_compressors=all_comp_sig,
        significant_markov=markov_sig,
        effect_size_bits_per_char=avg_effect
    )


def print_summary(results: List[HypothesisResult]):
    """Print summary of all hypothesis tests."""
    print("\n" + "="*90)
    print("HYPOTHESIS TEST SUMMARY")
    print("="*90)

    print("\n{:<18} {:>8} {:>12} {:>12} {:>12} {:>15}".format(
        "Encoding", "Length", "Density", "Effect", "Markov?", "Robust?"
    ))
    print("-"*90)

    for r in results:
        markov = "YES" if r.significant_markov else "no"
        robust = "YES" if r.significant_all_compressors else "no"
        print("{:<18} {:>8} {:>12.4f} {:>12.4f} {:>12} {:>15}".format(
            r.encoding, r.bitstring_length, r.density,
            r.effect_size_bits_per_char, markov, robust
        ))

    # Summary counts
    n_markov = sum(1 for r in results if r.significant_markov)
    n_robust = sum(1 for r in results if r.significant_all_compressors)

    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)
    print(f"\nTotal encodings tested: {len(results)}")
    print(f"Significant vs Markov surrogate: {n_markov}/{len(results)}")
    print(f"Robust across all compressors: {n_robust}/{len(results)}")

    if n_markov == 0:
        print("\n⚠️  NO encoding exceeds Markov baseline.")
        print("   All 'structure' is explainable by first-order transition probabilities.")
    elif n_robust == 0:
        print("\n⚠️  NO encoding is robust across compressors.")
        print("   Results may be compressor artifacts.")


def main():
    parser = argparse.ArgumentParser(description='Hypothesis testing for binary encodings')
    parser.add_argument('--encoding', type=str, default='all',
                        help='Encoding to test (or "all")')
    parser.add_argument('--nulls', type=str, default='all',
                        help='Null models to use (comma-separated or "all")')
    parser.add_argument('--perms', type=int, default=1000,
                        help='Number of permutations')
    parser.add_argument('--output', type=str, default='output/data/hypothesis_results.json',
                        help='Output file')
    args = parser.parse_args()

    # Load data
    print("Loading Quran...")
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")
    print(f"Loaded {len(text)} characters")

    # Determine which encodings to test
    if args.encoding == 'all':
        encodings = list(ALL_ENCODINGS.keys())
    else:
        encodings = [args.encoding]

    # Determine null models
    if args.nulls == 'all':
        null_models = list(NULL_MODELS.keys())
    else:
        null_models = args.nulls.split(',')

    print(f"\nTesting {len(encodings)} encoding(s)")
    print(f"Null models: {null_models}")
    print(f"Permutations: {args.perms}")
    print(f"Compressors: {list(COMPRESSORS.keys())}")

    # Run tests
    results = []
    for enc in encodings:
        result = test_encoding(enc, text, null_models, args.perms)
        results.append(result)

    # Print summary
    print_summary(results)

    # Save results
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump([asdict(r) for r in results], f, indent=2, default=str)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()

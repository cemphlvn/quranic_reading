"""
Main Pipeline: DATA → SEMANTIC → BINARY → MESSAGE → INTERPRETATION

Usage:
    python src/pipeline.py --encoding f_dot --scope full
    python src/pipeline.py --encoding f_dot --scope surah:1
    python src/pipeline.py --encoding f_dot --scope verse:1:5
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, analyze_bitstring,
    compare_with_null, interpret_as_existence, chunk_as_numbers
)
from encoding_functions.f_dot import encode_text as f_dot_encode, get_stats as f_dot_stats


ENCODERS = {
    'f_dot': (f_dot_encode, f_dot_stats),
}


def run_pipeline(encoding: str, scope: str, output_path: str = None):
    """
    Run the full pipeline.

    Args:
        encoding: Name of encoding function (e.g., 'f_dot')
        scope: Scope of analysis ('full', 'surah:N', 'verse:N:M')
        output_path: Optional path for JSON output
    """
    print("=" * 60)
    print("PATTERN-READING PIPELINE")
    print("=" * 60)
    print()

    # Stage 1: DATA
    print("[STAGE 1: DATA]")
    quran = load_quran("data/quran/quran.json")
    print(f"  Loaded: {len(quran)} surahs")

    text = extract_text(quran, scope)
    print(f"  Scope: {scope}")
    print(f"  Text length: {len(text)} characters")
    print()

    # Stage 2: SEMANTIC → BINARY
    print(f"[STAGE 2: SEMANTIC → BINARY ({encoding})]")

    if encoding not in ENCODERS:
        print(f"  ERROR: Unknown encoding '{encoding}'")
        print(f"  Available: {list(ENCODERS.keys())}")
        return

    encode_fn, stats_fn = ENCODERS[encoding]
    stats = stats_fn()
    print(f"  Encoding: {stats['description']}")
    print(f"  Baseline density: {stats.get('baseline_density', 'N/A'):.2%}")

    bitstring = encode_fn(text)
    print(f"  Bitstring length: {len(bitstring)}")
    print(f"  Sample: {bitstring[:80]}...")
    print()

    # Stage 3: MESSAGE ANALYSIS
    print("[STAGE 3: MESSAGE ANALYSIS]")
    analysis = analyze_bitstring(bitstring, f"{encoding}:{scope}")

    print(f"  Length: {analysis['length']}")
    print(f"  Density (1s): {analysis['density']:.4f}")
    print(f"  Entropy: {analysis['entropy']:.4f}")
    print(f"  Compression ratio: {analysis['compression_ratio']:.4f}")
    print(f"  Autocorrelation(1): {analysis['autocorrelation_1']:.4f}")
    print(f"  Max 0-run: {analysis['runs']['max_0_run']}")
    print(f"  Max 1-run: {analysis['runs']['max_1_run']}")
    print()

    # Stage 4: NULL COMPARISON
    print("[STAGE 4: NULL MODEL COMPARISON]")
    null_comparison = compare_with_null(bitstring, n_shuffles=50)

    print(f"  Real entropy: {null_comparison['real']['entropy']:.4f}")
    print(f"  Null mean entropy: {null_comparison['null_mean']['entropy']:.4f}")
    print(f"  Z-scores:")
    for k, v in null_comparison['z_scores'].items():
        sig = "***" if abs(v) > 2 else ""
        print(f"    {k}: {v:.2f} {sig}")

    if null_comparison['significant']:
        print("  >>> SIGNIFICANT DEVIATION FROM NULL <<<")
    else:
        print("  (No significant deviation)")
    print()

    # Stage 5: INTERPRETATION
    print("[STAGE 5: INTERPRETATION]")

    # Existence interpretation (sample)
    sample_bits = bitstring[:100]
    existence = interpret_as_existence(sample_bits)
    print(f"  First 100 bits as existence/void:")
    print(f"    {existence[:200]}...")

    # Numerical interpretation
    numbers = chunk_as_numbers(bitstring[:64], 8)
    print(f"  First 64 bits as 8-bit numbers: {numbers}")

    print()
    print("=" * 60)

    # Output
    result = {
        "encoding": encoding,
        "scope": scope,
        "stats": stats,
        "analysis": analysis,
        "null_comparison": null_comparison,
        "interpretation": {
            "existence_sample": existence[:500],
            "numbers_sample": numbers
        }
    }

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Results saved to: {output_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Pattern-Reading Pipeline")
    parser.add_argument("--encoding", "-e", default="f_dot",
                       help="Encoding function (default: f_dot)")
    parser.add_argument("--scope", "-s", default="full",
                       help="Scope: 'full', 'surah:N', 'verse:N:M'")
    parser.add_argument("--output", "-o", default=None,
                       help="Output JSON path")

    args = parser.parse_args()
    run_pipeline(args.encoding, args.scope, args.output)


if __name__ == "__main__":
    main()

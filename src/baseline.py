#!/usr/bin/env python3
"""
RANDOMNESS BASELINE REPORT

The only way to say "this pattern is real" is to ask:
"Is this more pattern than randomness usually creates?"

Model: i.i.d. Bernoulli(0.5) - fair coin flips
"""

import random
import zlib
from dataclasses import dataclass
from typing import List, Dict, Tuple, Callable
import sys

# ============================================================
# METRICS
# ============================================================

def metric_bit_balance(bits: str) -> float:
    """Percentage of 1s. Expected: 0.5 under fair coin."""
    if not bits:
        return 0.0
    return bits.count('1') / len(bits)


def metric_longest_run(bits: str) -> int:
    """Longest streak of identical bits."""
    if not bits:
        return 0
    max_run = 1
    current_run = 1
    for i in range(1, len(bits)):
        if bits[i] == bits[i-1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run


def metric_autocorr_lag1(bits: str) -> float:
    """
    Lag-1 autocorrelation: does bit[i] predict bit[i+1]?

    Returns correlation coefficient in [-1, 1].
    0 = no correlation (expected for i.i.d.)
    """
    if len(bits) < 2:
        return 0.0

    n = len(bits) - 1
    x = [int(b) for b in bits[:-1]]
    y = [int(b) for b in bits[1:]]

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denom_x = sum((xi - mean_x)**2 for xi in x) ** 0.5
    denom_y = sum((yi - mean_y)**2 for yi in y) ** 0.5

    if denom_x == 0 or denom_y == 0:
        return 0.0

    return numerator / (denom_x * denom_y)


def metric_pattern_entropy(bits: str) -> float:
    """
    2-bit pattern entropy.

    Measures how evenly distributed 00/01/10/11 patterns are.
    Max entropy = 2.0 (perfectly uniform)
    Lower = more biased toward certain patterns
    """
    import math
    if len(bits) < 2:
        return 0.0

    counts = {'00': 0, '01': 0, '10': 0, '11': 0}
    for i in range(len(bits) - 1):
        pattern = bits[i:i+2]
        counts[pattern] += 1

    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def metric_compression_ratio(bits: str) -> float:
    """
    Compression ratio using zlib.

    Lower = more compressible = more structure.
    Random bits: ~1.0 (incompressible)
    """
    if not bits:
        return 1.0
    data = bits.encode()
    compressed = zlib.compress(data, level=9)
    return len(compressed) / len(data)


# All metrics with their names and expected behavior
METRICS = {
    'bit_balance': (metric_bit_balance, 'higher_means_more_1s'),
    'longest_run': (metric_longest_run, 'higher_means_longer_streaks'),
    'autocorr_lag1': (metric_autocorr_lag1, 'away_from_zero_means_correlation'),
    'pattern_entropy': (metric_pattern_entropy, 'lower_means_more_biased'),
    'compression_ratio': (metric_compression_ratio, 'lower_means_more_structure'),
}


# ============================================================
# NULL DISTRIBUTION GENERATION
# ============================================================

def generate_random_bits(length: int, rng: random.Random) -> str:
    """Generate i.i.d. Bernoulli(0.5) bits."""
    return ''.join(rng.choice('01') for _ in range(length))


def build_null_distribution(
    length: int,
    n_samples: int = 10000,
    seed: int = 42,
    progress: bool = True
) -> Dict[str, List[float]]:
    """
    Build null distribution for all metrics.

    This is the "truth meter" - what randomness looks like.
    """
    rng = random.Random(seed)

    distributions = {name: [] for name in METRICS}

    for i in range(n_samples):
        if progress and (i + 1) % 1000 == 0:
            print(f"  Generating sample {i+1}/{n_samples}...", file=sys.stderr)

        bits = generate_random_bits(length, rng)

        for name, (fn, _) in METRICS.items():
            distributions[name].append(fn(bits))

    return distributions


# ============================================================
# ANALYSIS
# ============================================================

@dataclass
class MetricResult:
    """Result for one metric."""
    name: str
    observed: float
    null_mean: float
    null_std: float
    percentile: float  # What % of null samples are <= observed
    z_score: float
    interpretation: str


def compute_percentile(observed: float, distribution: List[float]) -> float:
    """What percentage of null samples are <= observed value."""
    count_below = sum(1 for x in distribution if x <= observed)
    return 100.0 * count_below / len(distribution)


def analyze_bitstring(
    bits: str,
    null_distributions: Dict[str, List[float]]
) -> List[MetricResult]:
    """
    Analyze a bitstring against the null distributions.

    Returns results for each metric.
    """
    results = []

    for name, (fn, behavior) in METRICS.items():
        observed = fn(bits)
        null_dist = null_distributions[name]

        null_mean = sum(null_dist) / len(null_dist)
        null_std = (sum((x - null_mean)**2 for x in null_dist) / len(null_dist)) ** 0.5

        percentile = compute_percentile(observed, null_dist)

        if null_std > 0:
            z_score = (observed - null_mean) / null_std
        else:
            z_score = 0.0

        # Interpretation
        if percentile < 2.5 or percentile > 97.5:
            interpretation = "RARE (p<0.05)"
        elif percentile < 5 or percentile > 95:
            interpretation = "UNUSUAL (p<0.10)"
        else:
            interpretation = "ORDINARY"

        results.append(MetricResult(
            name=name,
            observed=observed,
            null_mean=null_mean,
            null_std=null_std,
            percentile=percentile,
            z_score=z_score,
            interpretation=interpretation
        ))

    return results


# ============================================================
# REPORTING
# ============================================================

def format_report(
    label: str,
    length: int,
    results: List[MetricResult],
    n_samples: int
) -> str:
    """Format results as a clean report."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"RANDOMNESS BASELINE REPORT: {label}")
    lines.append("=" * 70)
    lines.append(f"Bitstring length: {length:,}")
    lines.append(f"Null model: i.i.d. Bernoulli(0.5) - fair coin flips")
    lines.append(f"Null samples: {n_samples:,}")
    lines.append("")
    lines.append("-" * 70)
    lines.append(f"{'Metric':<20} {'Observed':>12} {'Null Mean':>12} {'Null Std':>10} {'%ile':>8} {'Verdict':<12}")
    lines.append("-" * 70)

    for r in results:
        lines.append(
            f"{r.name:<20} {r.observed:>12.4f} {r.null_mean:>12.4f} {r.null_std:>10.4f} "
            f"{r.percentile:>7.1f}% {r.interpretation:<12}"
        )

    lines.append("-" * 70)
    lines.append("")

    # Summary
    rare_count = sum(1 for r in results if "RARE" in r.interpretation)
    unusual_count = sum(1 for r in results if "UNUSUAL" in r.interpretation)

    if rare_count > 0:
        lines.append(f"SUMMARY: {rare_count} metric(s) are RARE under pure randomness")
        lines.append("         This bitstring shows structure beyond fair-coin expectation.")
    elif unusual_count > 0:
        lines.append(f"SUMMARY: {unusual_count} metric(s) are UNUSUAL but not definitive")
        lines.append("         Mild deviation from randomness, investigate further.")
    else:
        lines.append("SUMMARY: All metrics are ORDINARY under pure randomness")
        lines.append("         This bitstring is consistent with fair coin flips.")

    lines.append("")
    return "\n".join(lines)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def run_baseline_report(
    bits: str,
    label: str = "Bitstring",
    n_samples: int = 10000,
    seed: int = 42,
    cache_null: Dict[str, List[float]] = None
) -> Tuple[str, Dict[str, List[float]]]:
    """
    Run complete baseline report.

    Returns (report_string, null_distributions).
    Null distributions can be cached for reuse.
    """
    length = len(bits)

    if cache_null is None:
        print(f"Building null distribution for length {length:,}...", file=sys.stderr)
        null_dist = build_null_distribution(length, n_samples, seed)
    else:
        null_dist = cache_null

    results = analyze_bitstring(bits, null_dist)
    report = format_report(label, length, results, n_samples)

    return report, null_dist


if __name__ == "__main__":
    # Quick test with random bits
    test_bits = generate_random_bits(10000, random.Random(123))
    report, _ = run_baseline_report(test_bits, "Random Test", n_samples=1000)
    print(report)

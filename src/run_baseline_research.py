#!/usr/bin/env python3
"""
RANDOMNESS BASELINE RESEARCH

Deliverable: "Which encodings produce bitstreams that deviate
from pure randomness more than expected?"
"""

import sys
import json
import random
import zlib
from datetime import datetime
from pathlib import Path

# ============================================================
# METRICS (inline for speed)
# ============================================================

def metric_bit_balance(bits):
    return bits.count('1') / len(bits) if bits else 0.0

def metric_longest_run(bits):
    if not bits:
        return 0
    max_run = current = 1
    for i in range(1, len(bits)):
        if bits[i] == bits[i-1]:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 1
    return max_run

def metric_autocorr(bits):
    if len(bits) < 2:
        return 0.0
    n = len(bits) - 1
    x = [int(b) for b in bits[:-1]]
    y = [int(b) for b in bits[1:]]
    mx, my = sum(x)/n, sum(y)/n
    num = sum((x[i]-mx)*(y[i]-my) for i in range(n))
    dx = sum((xi-mx)**2 for xi in x)**0.5
    dy = sum((yi-my)**2 for yi in y)**0.5
    return num/(dx*dy) if dx and dy else 0.0

def metric_compression(bits):
    if not bits:
        return 1.0
    data = bits.encode()
    return len(zlib.compress(data, 9)) / len(data)

METRICS = [
    ('bit_balance', metric_bit_balance),
    ('longest_run', metric_longest_run),
    ('autocorr', metric_autocorr),
    ('compression', metric_compression),
]

# ============================================================
# ENCODINGS (inline)
# ============================================================

import re
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

def enc_dotted(t):
    return ''.join('1' if c in DOTTED else '0' for c in extract(t) if c in DOTTED or c in UNDOTTED)

def enc_solar(t):
    return ''.join('1' if c in SOLAR else '0' for c in extract(t) if c in SOLAR or c in LUNAR)

def enc_voiced(t):
    return ''.join('1' if c in VOICED else '0' for c in extract(t) if c in VOICED or c in UNVOICED)

ENCODINGS = [
    ('dotted', enc_dotted, 'Dotted(1) vs Undotted(0)'),
    ('solar', enc_solar, 'Solar(1) vs Lunar(0)'),
    ('voiced', enc_voiced, 'Voiced(1) vs Unvoiced(0)'),
]

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("RANDOMNESS BASELINE RESEARCH")
    print("=" * 70)
    print()

    # Load Quran
    print("Loading Quran...")
    with open("data/quran/quran.json") as f:
        quran = json.load(f)
    text = " ".join(v["text"] for s in quran for v in s["verses"])
    print(f"  Text: {len(text):,} chars")
    print()

    # Apply encodings
    print("Applying encodings...")
    encoded = {}
    for name, fn, desc in ENCODINGS:
        bits = fn(text)
        encoded[name] = (bits, desc)
        print(f"  {name}: {len(bits):,} bits, balance={bits.count('1')/len(bits):.3f}")
    print()

    # Build null distribution
    N = 500  # Reduced for speed
    length = len(encoded['dotted'][0])
    print(f"Building null distribution (n={N}, length={length:,})...")

    rng = random.Random(42)
    null_dists = {m[0]: [] for m in METRICS}

    for i in range(N):
        if (i+1) % 100 == 0:
            print(f"  Sample {i+1}/{N}")
        rand_bits = ''.join(rng.choice('01') for _ in range(length))
        for name, fn in METRICS:
            null_dists[name].append(fn(rand_bits))
    print()

    # Analyze each encoding
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    results = []
    for enc_name, (bits, desc) in encoded.items():
        print(f"ENCODING: {enc_name} ({desc})")
        print("-" * 50)
        print(f"{'Metric':<15} {'Observed':>12} {'Null Mean':>12} {'%ile':>10} {'Verdict'}")
        print("-" * 50)

        enc_result = {'encoding': enc_name, 'description': desc, 'metrics': {}}
        rare_count = 0

        for metric_name, metric_fn in METRICS:
            observed = metric_fn(bits)
            null = null_dists[metric_name]
            null_mean = sum(null) / len(null)
            percentile = 100.0 * sum(1 for x in null if x <= observed) / len(null)

            if percentile < 2.5 or percentile > 97.5:
                verdict = "RARE"
                rare_count += 1
            elif percentile < 5 or percentile > 95:
                verdict = "UNUSUAL"
            else:
                verdict = "ordinary"

            print(f"{metric_name:<15} {observed:>12.4f} {null_mean:>12.4f} {percentile:>9.1f}% {verdict}")

            enc_result['metrics'][metric_name] = {
                'observed': observed,
                'null_mean': null_mean,
                'percentile': percentile,
                'verdict': verdict
            }

        enc_result['rare_count'] = rare_count
        results.append(enc_result)

        print("-" * 50)
        if rare_count >= 2:
            print(f"VERDICT: STRONG DEVIATION from randomness ({rare_count} rare metrics)")
        elif rare_count == 1:
            print(f"VERDICT: SOME DEVIATION from randomness ({rare_count} rare metric)")
        else:
            print("VERDICT: CONSISTENT with randomness")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY: WHICH ENCODINGS DEVIATE FROM PURE RANDOMNESS?")
    print("=" * 70)
    print()
    print(f"{'Encoding':<15} {'Rare Metrics':>15} {'Verdict'}")
    print("-" * 45)
    for r in results:
        if r['rare_count'] >= 2:
            v = "STRUCTURED"
        elif r['rare_count'] == 1:
            v = "WEAK SIGNAL"
        else:
            v = "RANDOM-LIKE"
        print(f"{r['encoding']:<15} {r['rare_count']:>15} {v}")
    print("-" * 45)
    print()
    print("Interpretation:")
    print("  STRUCTURED = Encoding captures real patterns in text")
    print("  WEAK SIGNAL = Marginal deviation, needs more samples")
    print("  RANDOM-LIKE = No evidence of structure beyond chance")
    print()

    # Save
    Path("output/data").mkdir(parents=True, exist_ok=True)
    with open("output/data/baseline_results.json", "w") as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'null_model': 'i.i.d. Bernoulli(0.5)',
            'n_samples': N,
            'results': results
        }, f, indent=2)
    print("Results saved to: output/data/baseline_results.json")

if __name__ == "__main__":
    main()

"""
RESEARCH ENGINE

Systematic, repeatable research on semantic-to-binary encodings.
Implements the formal methodology from docs/METHODOLOGY.md

This engine:
1. Defines multiple encoding functions
2. Defines multiple interpretation functions
3. Runs systematic experiments
4. Records results in structured format
5. Repeats until convergence
"""

import sys
import json
import random
import math
import re
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List, Any, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, shannon_entropy, compression_ratio,
    density, run_length_analysis, autocorrelation
)


# ============================================================
# FORMAL DEFINITIONS
# ============================================================

@dataclass
class EncodingResult:
    """Result of applying an encoding function."""
    encoding_name: str
    bitstring: str
    length: int
    density: float
    entropy: float
    compression: float
    max_run_0: int
    max_run_1: int
    total_runs: int
    autocorr_1: float


@dataclass
class NullTestResult:
    """Result of null hypothesis test."""
    z_compression: float
    z_entropy: float
    z_autocorr: float
    p_value: float  # Two-tailed p-value from z-score
    significant_raw: bool  # Before Bonferroni (α=0.05)
    significant_corrected: bool  # After Bonferroni (α=0.003125 for k=16)
    p_estimate: str


@dataclass
class InterpretationResult:
    """Result of interpretation function."""
    method: str
    output: Any
    pattern_found: bool
    description: str


@dataclass
class ExperimentResult:
    """Complete experiment result."""
    encoding: EncodingResult
    null_test: NullTestResult
    interpretations: List[InterpretationResult]
    verdict: str
    valid: bool


# ============================================================
# ENCODING FUNCTIONS
# ============================================================

def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics."""
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    return diacritics.sub('', text)


def extract_letters(text: str) -> List[str]:
    """Extract Arabic letters only."""
    arabic = re.compile(r'[\u0621-\u064A]')
    return [c for c in strip_diacritics(text) if arabic.match(c)]


# E1: Dot encoding
DOT_MAP = {
    'ب': 1, 'ت': 1, 'ث': 1, 'ج': 1, 'خ': 1, 'ذ': 1, 'ز': 1,
    'ش': 1, 'ض': 1, 'ظ': 1, 'غ': 1, 'ف': 1, 'ق': 1, 'ن': 1, 'ي': 1,
    'ا': 0, 'ح': 0, 'د': 0, 'ر': 0, 'س': 0, 'ص': 0, 'ط': 0,
    'ع': 0, 'ك': 0, 'ل': 0, 'م': 0, 'ه': 0, 'و': 0,
    'ء': 0, 'أ': 0, 'إ': 0, 'آ': 0, 'ؤ': 0, 'ئ': 0, 'ة': 0, 'ى': 0,
}

def encode_dot(text: str) -> str:
    """E1: Dotted=1, undotted=0."""
    return ''.join(str(DOT_MAP.get(c, '')) for c in extract_letters(text))


# E2: Voice encoding
VOICED = set('بدضذزظغعمنلروي')
def encode_voice(text: str) -> str:
    """E2: Voiced=1, voiceless=0."""
    return ''.join('1' if c in VOICED else '0' for c in extract_letters(text) if c in DOT_MAP)


# E3: Emphasis encoding
EMPHATIC = set('صضطظق')
def encode_emphasis(text: str) -> str:
    """E3: Emphatic=1, plain=0."""
    return ''.join('1' if c in EMPHATIC else '0' for c in extract_letters(text) if c in DOT_MAP)


# E4: Throat encoding (guttural consonants)
THROAT = set('ءأإآعغحخهق')
def encode_throat(text: str) -> str:
    """E4: Throat/guttural=1, else=0."""
    return ''.join('1' if c in THROAT else '0' for c in extract_letters(text) if c in DOT_MAP)


# E5: Connectivity encoding
NON_CONNECTORS = set('اأإآءؤدذرزو')
def encode_connect(text: str) -> str:
    """E5: Connects-left=1, non-connector=0."""
    return ''.join('0' if c in NON_CONNECTORS else '1' for c in extract_letters(text) if c in DOT_MAP)


# E6: Abjad parity encoding
ABJAD = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
    'ي': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90,
    'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
    'ء': 1, 'أ': 1, 'إ': 1, 'آ': 1, 'ؤ': 6, 'ئ': 10, 'ة': 5, 'ى': 10,
}

def encode_abjad_parity(text: str) -> str:
    """E6: Odd abjad=1, even=0."""
    return ''.join(str(ABJAD.get(c, 0) % 2) for c in extract_letters(text) if c in ABJAD)


# E7: Abjad prime encoding
def is_prime(n: int) -> bool:
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

PRIME_ABJAD = {k for k, v in ABJAD.items() if is_prime(v)}

def encode_abjad_prime(text: str) -> str:
    """E7: Prime abjad value=1, else=0."""
    return ''.join('1' if c in PRIME_ABJAD else '0' for c in extract_letters(text) if c in ABJAD)


# E8: Solar/Lunar encoding (for lam assimilation)
SOLAR = set('تثدذرزسشصضطظنل')
def encode_solar(text: str) -> str:
    """E8: Solar letter=1, lunar=0."""
    return ''.join('1' if c in SOLAR else '0' for c in extract_letters(text) if c in DOT_MAP)


# All encodings
ENCODINGS = {
    'E1_dot': encode_dot,
    'E2_voice': encode_voice,
    'E3_emphasis': encode_emphasis,
    'E4_throat': encode_throat,
    'E5_connect': encode_connect,
    'E6_abjad_parity': encode_abjad_parity,
    'E7_abjad_prime': encode_abjad_prime,
    'E8_solar': encode_solar,
}


# ============================================================
# INTERPRETATION FUNCTIONS
# ============================================================

def interpret_stats(bitstring: str) -> InterpretationResult:
    """I_stat: Statistical properties."""
    d = density(bitstring)
    e = shannon_entropy(bitstring)
    c = compression_ratio(bitstring)
    runs = run_length_analysis(bitstring)

    pattern = c < 0.16  # highly compressible = pattern
    desc = f"density={d:.3f}, entropy={e:.3f}, compression={c:.3f}"

    return InterpretationResult(
        method="I_stat",
        output={"density": d, "entropy": e, "compression": c, "runs": runs['total_runs']},
        pattern_found=pattern,
        description=desc
    )


def interpret_chunks(bitstring: str, k: int = 8) -> InterpretationResult:
    """I_chunk: Read as k-bit integers."""
    numbers = []
    for i in range(0, len(bitstring) - k + 1, k):
        chunk = bitstring[i:i+k]
        numbers.append(int(chunk, 2))

    # Check for patterns in numbers
    if len(numbers) > 10:
        diffs = [numbers[i+1] - numbers[i] for i in range(min(100, len(numbers)-1))]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        pattern = abs(avg_diff) < 10  # small average difference = pattern
    else:
        pattern = False

    return InterpretationResult(
        method=f"I_chunk({k})",
        output=numbers[:20],  # first 20
        pattern_found=pattern,
        description=f"First 20 values: {numbers[:20]}"
    )


def interpret_runs(bitstring: str) -> InterpretationResult:
    """I_run: Run-length encoding."""
    if not bitstring:
        return InterpretationResult("I_run", [], False, "Empty")

    runs = []
    current = bitstring[0]
    length = 1

    for bit in bitstring[1:]:
        if bit == current:
            length += 1
        else:
            runs.append((int(current), length))
            current = bit
            length = 1
    runs.append((int(current), length))

    # Pattern: are run lengths following a distribution?
    lengths = [r[1] for r in runs]
    mean_len = sum(lengths) / len(lengths)
    max_len = max(lengths)

    pattern = max_len > mean_len * 5  # unusually long runs

    return InterpretationResult(
        method="I_run",
        output={"mean_run": mean_len, "max_run": max_len, "n_runs": len(runs)},
        pattern_found=pattern,
        description=f"mean_run={mean_len:.2f}, max_run={max_len}"
    )


def interpret_mod19(bitstring: str) -> InterpretationResult:
    """I_mod19: Check for patterns related to 19 (Code 19 hypothesis)."""
    # Count 1s in chunks of 19
    counts = []
    for i in range(0, len(bitstring) - 19 + 1, 19):
        chunk = bitstring[i:i+19]
        counts.append(chunk.count('1'))

    if not counts:
        return InterpretationResult("I_mod19", {}, False, "Too short")

    mean_count = sum(counts) / len(counts)

    # Check if total 1s is divisible by 19
    total_1s = bitstring.count('1')
    div_19 = total_1s % 19 == 0

    return InterpretationResult(
        method="I_mod19",
        output={"total_1s": total_1s, "div_by_19": div_19, "remainder": total_1s % 19},
        pattern_found=div_19,
        description=f"total_1s={total_1s}, mod_19={total_1s % 19}"
    )


def interpret_palindrome(bitstring: str) -> InterpretationResult:
    """I_palindrome: Search for palindromic patterns."""
    # Search for palindromic substrings
    max_palindrome = 0
    sample = bitstring[:10000]  # search in first 10k

    for length in [10, 20, 50, 100]:
        for i in range(len(sample) - length):
            sub = sample[i:i+length]
            if sub == sub[::-1]:
                max_palindrome = max(max_palindrome, length)

    pattern = max_palindrome >= 20

    return InterpretationResult(
        method="I_palindrome",
        output={"max_palindrome_length": max_palindrome},
        pattern_found=pattern,
        description=f"max_palindrome={max_palindrome}"
    )


INTERPRETATIONS = [
    interpret_stats,
    lambda b: interpret_chunks(b, 8),
    interpret_runs,
    interpret_mod19,
    interpret_palindrome,
]


# ============================================================
# NULL HYPOTHESIS TESTING
# ============================================================

# Statistical constants
N_ENCODINGS = 16  # Number of encodings tested
ALPHA = 0.05  # Base significance level
ALPHA_CORRECTED = ALPHA / N_ENCODINGS  # Bonferroni: 0.003125
Z_THRESHOLD_RAW = 1.96  # |z| for α=0.05 two-tailed
Z_THRESHOLD_CORRECTED = 2.96  # |z| for α=0.003125 two-tailed


def z_to_p(z: float) -> float:
    """Convert z-score to two-tailed p-value using normal approximation."""
    # Using error function approximation
    import math
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def null_test(bitstring: str, n_shuffles: int = 1000) -> NullTestResult:
    """
    Test against null model (shuffled bitstring).

    Uses 1000 shuffle iterations for stable z-scores.
    Reports both raw and Bonferroni-corrected significance.
    """
    real_comp = compression_ratio(bitstring)
    real_ent = shannon_entropy(bitstring)
    real_ac = autocorrelation(bitstring, 1)

    null_comp, null_ent, null_ac = [], [], []
    bits = list(bitstring)

    for _ in range(n_shuffles):
        random.shuffle(bits)
        shuffled = ''.join(bits)
        null_comp.append(compression_ratio(shuffled))
        null_ent.append(shannon_entropy(shuffled))
        null_ac.append(autocorrelation(shuffled, 1))

    def z_score(real, nulls):
        mean = sum(nulls) / len(nulls)
        std = (sum((x - mean)**2 for x in nulls) / len(nulls)) ** 0.5
        return (real - mean) / std if std > 0 else 0

    z_c = z_score(real_comp, null_comp)
    z_e = z_score(real_ent, null_ent)
    z_a = z_score(real_ac, null_ac)

    # Use most significant z-score for p-value
    z_max = max(abs(z_c), abs(z_e), abs(z_a))
    p_val = z_to_p(z_max)

    # Significance tests
    sig_raw = z_max > Z_THRESHOLD_RAW
    sig_corrected = z_max > Z_THRESHOLD_CORRECTED

    # Human-readable p-value
    if p_val < 0.0001:
        p_est = f"p < 0.0001 (z={z_max:.2f})"
    elif p_val < ALPHA_CORRECTED:
        p_est = f"p = {p_val:.4f} < {ALPHA_CORRECTED:.4f} (corrected)"
    elif p_val < ALPHA:
        p_est = f"p = {p_val:.4f} < 0.05 (uncorrected only)"
    else:
        p_est = f"p = {p_val:.4f} (not significant)"

    return NullTestResult(z_c, z_e, z_a, p_val, sig_raw, sig_corrected, p_est)


# ============================================================
# MAIN RESEARCH ENGINE
# ============================================================

def run_experiment(encoding_name: str, encode_fn: Callable, text: str) -> ExperimentResult:
    """Run complete experiment for one encoding."""
    # Encode
    bitstring = encode_fn(text)
    if len(bitstring) < 100:
        return None

    runs = run_length_analysis(bitstring)

    enc_result = EncodingResult(
        encoding_name=encoding_name,
        bitstring=bitstring[:100] + "...",  # sample
        length=len(bitstring),
        density=density(bitstring),
        entropy=shannon_entropy(bitstring),
        compression=compression_ratio(bitstring),
        max_run_0=runs['max_0_run'],
        max_run_1=runs['max_1_run'],
        total_runs=runs['total_runs'],
        autocorr_1=autocorrelation(bitstring, 1)
    )

    # Null test
    null_result = null_test(bitstring)

    # Interpretations
    interp_results = [fn(bitstring) for fn in INTERPRETATIONS]

    # Verdict (use Bonferroni-corrected significance)
    if null_result.significant_corrected:
        verdict = "SIGNIFICANT (corrected)"
        valid = True
    elif null_result.significant_raw:
        verdict = "SIGNIFICANT (uncorrected)"
        valid = False  # Not valid under strict criteria
    else:
        verdict = "NOT SIGNIFICANT"
        valid = False

    return ExperimentResult(enc_result, null_result, interp_results, verdict, valid)


def run_all_experiments(text: str) -> List[ExperimentResult]:
    """Run experiments for all encodings."""
    results = []
    for name, fn in ENCODINGS.items():
        result = run_experiment(name, fn, text)
        if result:
            results.append(result)
    return results


def print_results(results: List[ExperimentResult]):
    """Print formatted results."""
    print("\n" + "="*90)
    print("RESEARCH ENGINE: SYSTEMATIC ENCODING ANALYSIS")
    print(f"Statistical threshold: |z| > {Z_THRESHOLD_CORRECTED:.2f} (Bonferroni α={ALPHA_CORRECTED:.4f})")
    print("="*90)

    print("\n{:<18} {:>8} {:>8} {:>10} {:>12} {:>25}".format(
        "Encoding", "Length", "Density", "Compress", "Z-score", "Verdict"
    ))
    print("-"*90)

    for r in results:
        print("{:<18} {:>8} {:>8.4f} {:>10.4f} {:>12.2f} {:>25}".format(
            r.encoding.encoding_name,
            r.encoding.length,
            r.encoding.density,
            r.encoding.compression,
            r.null_test.z_compression,
            r.verdict
        ))

    print("\n" + "="*80)
    print("DETAILED INTERPRETATION RESULTS")
    print("="*80)

    for r in results:
        if r.valid:
            print(f"\n### {r.encoding.encoding_name} ###")
            for i in r.interpretations:
                flag = "✓" if i.pattern_found else "✗"
                print(f"  {flag} {i.method}: {i.description}")

    # Summary
    valid = [r for r in results if r.valid]
    print("\n" + "="*80)
    print(f"SUMMARY: {len(valid)}/{len(results)} encodings show significant structure")
    print("="*80)

    if valid:
        print("\nEncodings with structure:")
        for r in valid:
            print(f"  - {r.encoding.encoding_name}: z={r.null_test.z_compression:.2f}")


def main():
    """Main research loop."""
    # Load data
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")
    print(f"Loaded Quran: {len(text)} characters")

    # Run all experiments
    results = run_all_experiments(text)

    # Print results
    print_results(results)

    # Save to JSON
    output = []
    for r in results:
        output.append({
            "encoding": asdict(r.encoding),
            "null_test": asdict(r.null_test),
            "interpretations": [asdict(i) for i in r.interpretations],
            "verdict": r.verdict,
            "valid": r.valid
        })

    Path("output/data").mkdir(parents=True, exist_ok=True)
    with open("output/data/experiment_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to output/data/experiment_results.json")

    return results


if __name__ == "__main__":
    main()

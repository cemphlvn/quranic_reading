"""
Binary Message Analysis Framework

Given any f: Text → Binary, this module analyzes the resulting bitstring
for non-random structure that could constitute a "message".

The question: To be (1) or not to be (0)?
"""

import json
import math
from collections import Counter
from typing import Callable, List, Dict, Tuple, Any
import re


def load_quran(path: str = "data/quran/quran.json") -> List[Dict]:
    """Load Quran from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_text(quran: List[Dict], level: str = "full") -> str:
    """
    Extract text at specified level.
    level: "full" | "surah:N" | "verse:N:M"
    """
    if level == "full":
        return " ".join(
            verse["text"]
            for surah in quran
            for verse in surah["verses"]
        )
    elif level.startswith("surah:"):
        n = int(level.split(":")[1])
        return " ".join(v["text"] for v in quran[n-1]["verses"])
    elif level.startswith("verse:"):
        parts = level.split(":")
        s, v = int(parts[1]), int(parts[2])
        return quran[s-1]["verses"][v-1]["text"]
    return ""


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics (harakat)."""
    diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')
    return diacritics.sub('', text)


def extract_letters(text: str) -> str:
    """Extract only Arabic letters, no spaces or punctuation."""
    arabic_letters = re.compile(r'[\u0621-\u064A]')
    return ''.join(arabic_letters.findall(strip_diacritics(text)))


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def shannon_entropy(bitstring: str) -> float:
    """Compute Shannon entropy of bitstring."""
    if not bitstring:
        return 0.0
    counts = Counter(bitstring)
    total = len(bitstring)
    entropy = -sum(
        (c/total) * math.log2(c/total)
        for c in counts.values() if c > 0
    )
    return entropy


def run_length_analysis(bitstring: str) -> Dict[str, Any]:
    """Analyze runs of consecutive 0s and 1s."""
    if not bitstring:
        return {"runs": [], "max_0": 0, "max_1": 0, "avg_run": 0}

    runs = []
    current = bitstring[0]
    length = 1

    for bit in bitstring[1:]:
        if bit == current:
            length += 1
        else:
            runs.append((current, length))
            current = bit
            length = 1
    runs.append((current, length))

    zeros = [r[1] for r in runs if r[0] == '0']
    ones = [r[1] for r in runs if r[0] == '1']

    return {
        "total_runs": len(runs),
        "max_0_run": max(zeros) if zeros else 0,
        "max_1_run": max(ones) if ones else 0,
        "avg_0_run": sum(zeros)/len(zeros) if zeros else 0,
        "avg_1_run": sum(ones)/len(ones) if ones else 0,
        "run_distribution": Counter([r[1] for r in runs])
    }


def density(bitstring: str) -> float:
    """Ratio of 1s to total bits."""
    if not bitstring:
        return 0.0
    return bitstring.count('1') / len(bitstring)


def autocorrelation(bitstring: str, lag: int = 1) -> float:
    """Compute autocorrelation at given lag."""
    if len(bitstring) <= lag:
        return 0.0

    bits = [int(b) for b in bitstring]
    n = len(bits)
    mean = sum(bits) / n

    numerator = sum(
        (bits[i] - mean) * (bits[i + lag] - mean)
        for i in range(n - lag)
    )
    denominator = sum((b - mean) ** 2 for b in bits)

    if denominator == 0:
        return 0.0
    return numerator / denominator


def compression_ratio(bitstring: str) -> float:
    """Estimate compressibility (lower = more structure)."""
    import zlib
    if not bitstring:
        return 1.0
    original = len(bitstring.encode())
    compressed = len(zlib.compress(bitstring.encode()))
    return compressed / original


def pattern_search(bitstring: str, pattern: str) -> List[int]:
    """Find all occurrences of a pattern."""
    indices = []
    start = 0
    while True:
        idx = bitstring.find(pattern, start)
        if idx == -1:
            break
        indices.append(idx)
        start = idx + 1
    return indices


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_bitstring(bitstring: str, label: str = "") -> Dict[str, Any]:
    """
    Full analysis of a bitstring.
    Returns metrics that reveal non-random structure.
    """
    return {
        "label": label,
        "length": len(bitstring),
        "density": density(bitstring),
        "entropy": shannon_entropy(bitstring),
        "compression_ratio": compression_ratio(bitstring),
        "runs": run_length_analysis(bitstring),
        "autocorrelation_1": autocorrelation(bitstring, 1),
        "autocorrelation_2": autocorrelation(bitstring, 2),
        "sample": bitstring[:100] + "..." if len(bitstring) > 100 else bitstring
    }


def compare_with_null(bitstring: str, n_shuffles: int = 100) -> Dict[str, Any]:
    """
    Compare bitstring with shuffled versions (null model).
    If real bitstring differs significantly, structure exists.
    """
    import random

    real_metrics = {
        "entropy": shannon_entropy(bitstring),
        "compression": compression_ratio(bitstring),
        "autocorr": autocorrelation(bitstring, 1)
    }

    null_metrics = {"entropy": [], "compression": [], "autocorr": []}
    bits = list(bitstring)

    for _ in range(n_shuffles):
        random.shuffle(bits)
        shuffled = ''.join(bits)
        null_metrics["entropy"].append(shannon_entropy(shuffled))
        null_metrics["compression"].append(compression_ratio(shuffled))
        null_metrics["autocorr"].append(autocorrelation(shuffled, 1))

    def z_score(real, nulls):
        mean = sum(nulls) / len(nulls)
        std = (sum((x - mean)**2 for x in nulls) / len(nulls)) ** 0.5
        if std == 0:
            return 0
        return (real - mean) / std

    return {
        "real": real_metrics,
        "null_mean": {k: sum(v)/len(v) for k, v in null_metrics.items()},
        "z_scores": {
            k: z_score(real_metrics[k], null_metrics[k])
            for k in real_metrics
        },
        "significant": any(
            abs(z_score(real_metrics[k], null_metrics[k])) > 2
            for k in real_metrics
        )
    }


# ============================================================
# MESSAGE INTERPRETATION
# ============================================================

def interpret_as_existence(bitstring: str) -> str:
    """
    Interpret bitstring as existence/non-existence message.
    1 = "be" (wujud)
    0 = "not-be" (adam)
    """
    mapping = {'1': 'BE', '0': 'VOID'}
    # Group into meaningful chunks (runs)
    runs = []
    if not bitstring:
        return ""

    current = bitstring[0]
    length = 1
    for bit in bitstring[1:]:
        if bit == current:
            length += 1
        else:
            runs.append((mapping[current], length))
            current = bit
            length = 1
    runs.append((mapping[current], length))

    # Format as readable message
    return " ".join(f"{state}×{count}" for state, count in runs)


def chunk_as_numbers(bitstring: str, chunk_size: int = 8) -> List[int]:
    """Interpret bitstring as sequence of numbers."""
    numbers = []
    for i in range(0, len(bitstring), chunk_size):
        chunk = bitstring[i:i+chunk_size]
        if len(chunk) == chunk_size:
            numbers.append(int(chunk, 2))
    return numbers


if __name__ == "__main__":
    # Quick test
    test = "110100110011010011001100"
    print("Test bitstring:", test)
    print("Analysis:", analyze_bitstring(test, "test"))
    print("Existence interpretation:", interpret_as_existence(test))

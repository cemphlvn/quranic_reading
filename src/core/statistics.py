"""
STATISTICAL TESTING

Proper hypothesis testing infrastructure.
- Permutation p-values (not z-scores)
- Multiple compressors
- Effect sizes in bits/char
"""

import zlib
import bz2
import lzma
from typing import Dict, List, Callable, Any
from dataclasses import dataclass


# ============================================================
# COMPRESSION FUNCTIONS
# ============================================================

def compress_zlib(data: bytes) -> int:
    """Compress with zlib, return compressed size."""
    return len(zlib.compress(data, level=9))


def compress_bz2(data: bytes) -> int:
    """Compress with bzip2, return compressed size."""
    return len(bz2.compress(data, compresslevel=9))


def compress_lzma(data: bytes) -> int:
    """Compress with lzma, return compressed size."""
    return len(lzma.compress(data))


COMPRESSORS = {
    'zlib': compress_zlib,
    'bz2': compress_bz2,
    'lzma': compress_lzma,
}


def compression_ratio(bits: str, compressor: str = 'zlib') -> float:
    """Compute compression ratio using specified compressor."""
    if not bits:
        return 1.0
    data = bits.encode()
    original = len(data)
    compressed = COMPRESSORS[compressor](data)
    return compressed / original


def compression_all(bits: str) -> Dict[str, float]:
    """Compute compression ratio with all compressors."""
    return {name: compression_ratio(bits, name) for name in COMPRESSORS}


# ============================================================
# EFFECT SIZE
# ============================================================

def effect_size_bits(observed_cr: float, null_cr: float, length: int) -> float:
    """
    Compute effect size in bits.

    Δ_bits = (null_cr - observed_cr) * length * 8

    Positive = observed is more compressible (more structure)
    """
    return (null_cr - observed_cr) * length * 8


def effect_size_bits_per_char(observed_cr: float, null_cr: float) -> float:
    """
    Compute effect size in bits per character.

    More interpretable than total bits.
    """
    return (null_cr - observed_cr) * 8


# ============================================================
# PERMUTATION P-VALUE
# ============================================================

@dataclass
class PermutationResult:
    """Result of permutation test."""
    observed: float
    null_mean: float
    null_std: float
    p_value: float  # Exact permutation p-value
    effect_bits: float  # Effect size in bits
    effect_bits_per_char: float
    n_permutations: int
    compressor: str
    null_model: str


def permutation_test(
    bits: str,
    null_fn: Callable[[str], str],
    n_perms: int = 1000,
    compressor: str = 'zlib',
    null_model_name: str = 'unknown'
) -> PermutationResult:
    """
    Proper permutation test.

    Returns exact permutation p-value, not z-score approximation.
    p = (count(null >= observed) + 1) / (N + 1)
    """
    observed_cr = compression_ratio(bits, compressor)
    length = len(bits)

    null_crs = []
    count_as_extreme = 0

    for _ in range(n_perms):
        null_bits = null_fn(bits)
        null_cr = compression_ratio(null_bits, compressor)
        null_crs.append(null_cr)

        # Count how many nulls are as extreme (lower CR = more structure)
        if null_cr <= observed_cr:
            count_as_extreme += 1

    # Exact permutation p-value
    p_value = (count_as_extreme + 1) / (n_perms + 1)

    # Null statistics
    null_mean = sum(null_crs) / len(null_crs)
    null_std = (sum((x - null_mean)**2 for x in null_crs) / len(null_crs)) ** 0.5

    # Effect sizes
    effect_total = effect_size_bits(observed_cr, null_mean, length)
    effect_per_char = effect_size_bits_per_char(observed_cr, null_mean)

    return PermutationResult(
        observed=observed_cr,
        null_mean=null_mean,
        null_std=null_std,
        p_value=p_value,
        effect_bits=effect_total,
        effect_bits_per_char=effect_per_char,
        n_permutations=n_perms,
        compressor=compressor,
        null_model=null_model_name
    )


# ============================================================
# MULTI-COMPRESSOR TEST
# ============================================================

def test_compressor_robustness(
    bits: str,
    null_fn: Callable[[str], str],
    n_perms: int = 1000,
    null_model_name: str = 'unknown'
) -> Dict[str, PermutationResult]:
    """
    Test with all compressors.

    If effect only appears with one compressor → compressor quirk.
    """
    results = {}
    for compressor in COMPRESSORS:
        results[compressor] = permutation_test(
            bits, null_fn, n_perms, compressor, null_model_name
        )
    return results


def is_robust_across_compressors(results: Dict[str, PermutationResult], alpha: float = 0.05) -> bool:
    """Check if result is significant across all compressors."""
    return all(r.p_value < alpha for r in results.values())


# ============================================================
# BONFERRONI CORRECTION
# ============================================================

def bonferroni_threshold(alpha: float, n_tests: int) -> float:
    """Compute Bonferroni-corrected alpha."""
    return alpha / n_tests


def is_significant_corrected(p_value: float, alpha: float, n_tests: int) -> bool:
    """Check if p-value is significant after Bonferroni correction."""
    return p_value < bonferroni_threshold(alpha, n_tests)

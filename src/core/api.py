"""
CORE API - Self-Validating Research Infrastructure

All tests MUST go through this API. No escape from methodology.

Key insight: The question is "beyond word boundaries?"
- Critical null: WORD PERMUTATION (keeps words, shuffles order)
- Diagnostic: BLOCK SHUFFLE CURVE (reveals length-scale)
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple, Optional, Any
from enum import Enum
import random


# ============================================================
# TYPES
# ============================================================

class NullType(Enum):
    """Where the null operates."""
    TEXT = "text"  # Transforms text, respects language units
    BITS = "bits"  # Transforms bits directly


class MetricDirection(Enum):
    """Which direction indicates more structure."""
    LOWER = "lower"  # Lower = more structure (compression ratio)
    HIGHER = "higher"  # Higher = more structure (mutual info)


# ============================================================
# REGISTRY METADATA
# ============================================================

@dataclass(frozen=True)
class EncodingMeta:
    """Encoding function metadata."""
    name: str
    fn: Callable[[str], str]  # text -> bits
    description: str
    hypothesis: str  # What this encoding tests
    preregistered: bool = False


@dataclass(frozen=True)
class NullMeta:
    """Null model metadata."""
    name: str
    fn: Callable  # Signature varies by type
    null_type: NullType
    preserves: str  # What it preserves
    destroys: str  # What it destroys


@dataclass(frozen=True)
class MetricMeta:
    """Metric function metadata."""
    name: str
    fn: Callable[[str], float]  # bits -> float
    direction: MetricDirection
    description: str


@dataclass(frozen=True)
class CorpusMeta:
    """Corpus metadata."""
    name: str
    text: str
    source: str
    language: str


# ============================================================
# GLOBAL REGISTRIES
# ============================================================

ENCODINGS: Dict[str, EncodingMeta] = {}
NULLS: Dict[str, NullMeta] = {}
METRICS: Dict[str, MetricMeta] = {}
CORPORA: Dict[str, CorpusMeta] = {}


# ============================================================
# REGISTRATION FUNCTIONS
# ============================================================

def register_encoding(
    name: str,
    fn: Callable[[str], str],
    description: str,
    hypothesis: str,
    preregistered: bool = False
) -> EncodingMeta:
    """
    Register an encoding function.

    Args:
        name: Unique identifier (e.g., "E8_solar")
        fn: Function text -> bits
        description: What it does
        hypothesis: What it tests
        preregistered: Was hypothesis written before seeing results?
    """
    # Validate function signature
    test_result = fn("test")
    if not isinstance(test_result, str) or not all(c in '01' for c in test_result):
        raise ValueError(f"Encoding {name} must return string of 0s and 1s")

    meta = EncodingMeta(name, fn, description, hypothesis, preregistered)
    ENCODINGS[name] = meta
    return meta


def register_null(
    name: str,
    fn: Callable,
    null_type: NullType,
    preserves: str,
    destroys: str
) -> NullMeta:
    """
    Register a null model.

    Args:
        name: Unique identifier (e.g., "word_perm")
        fn: Null function
        null_type: TEXT or BITS
        preserves: What structure it preserves
        destroys: What structure it destroys
    """
    meta = NullMeta(name, fn, null_type, preserves, destroys)
    NULLS[name] = meta
    return meta


def register_metric(
    name: str,
    fn: Callable[[str], float],
    direction: MetricDirection,
    description: str
) -> MetricMeta:
    """
    Register a metric function.

    Args:
        name: Unique identifier (e.g., "compression_zlib")
        fn: Function bits -> float
        direction: LOWER or HIGHER indicates more structure
        description: What it measures
    """
    meta = MetricMeta(name, fn, direction, description)
    METRICS[name] = meta
    return meta


def register_corpus(
    name: str,
    text: str,
    source: str,
    language: str = "Arabic"
) -> CorpusMeta:
    """Register a text corpus."""
    if not text:
        raise ValueError(f"Corpus {name} cannot be empty")
    meta = CorpusMeta(name, text, source, language)
    CORPORA[name] = meta
    return meta


# ============================================================
# NULL MODEL IMPLEMENTATIONS
# ============================================================

def null_word_permutation(text: str, rng: random.Random) -> str:
    """
    THE critical null for "beyond word boundaries".

    Keeps words intact, shuffles word order.
    If encoding beats this → cross-word structure exists.
    """
    words = text.split()
    rng.shuffle(words)
    return ' '.join(words)


def null_block_shuffle_letters(text: str, block_size: int, rng: random.Random) -> str:
    """
    Block shuffle at letter level (preserving word boundaries marker).

    For length-scale diagnostic.
    """
    # Separate words
    words = text.split()
    result_words = []

    for word in words:
        letters = list(word)
        if len(letters) <= block_size:
            # Word smaller than block → keep intact
            result_words.append(word)
        else:
            # Shuffle blocks within word
            blocks = [letters[i:i+block_size] for i in range(0, len(letters), block_size)]
            rng.shuffle(blocks)
            result_words.append(''.join(''.join(b) for b in blocks))

    return ' '.join(result_words)


def null_random_shuffle_bits(bits: str, rng: random.Random) -> str:
    """Shuffle all bits randomly. Preserves only 0/1 ratio."""
    bits_list = list(bits)
    rng.shuffle(bits_list)
    return ''.join(bits_list)


def null_block_shuffle_bits(bits: str, block_size: int, rng: random.Random) -> str:
    """Shuffle blocks of bits. Preserves local patterns."""
    blocks = [bits[i:i+block_size] for i in range(0, len(bits), block_size)]
    rng.shuffle(blocks)
    return ''.join(blocks)


# ============================================================
# METRIC IMPLEMENTATIONS
# ============================================================

import zlib
import bz2
import lzma


def metric_compression_zlib(bits: str) -> float:
    """Compression ratio using zlib."""
    if not bits:
        return 1.0
    data = bits.encode()
    return len(zlib.compress(data, level=9)) / len(data)


def metric_compression_bz2(bits: str) -> float:
    """Compression ratio using bz2."""
    if not bits:
        return 1.0
    data = bits.encode()
    return len(bz2.compress(data, compresslevel=9)) / len(data)


def metric_compression_lzma(bits: str) -> float:
    """Compression ratio using lzma."""
    if not bits:
        return 1.0
    data = bits.encode()
    return len(lzma.compress(data)) / len(data)


# ============================================================
# REGISTER BUILT-IN NULLS AND METRICS
# ============================================================

def _init_builtins():
    """Register built-in nulls and metrics."""
    # Critical null
    register_null(
        "word_perm",
        null_word_permutation,
        NullType.TEXT,
        preserves="Words intact, within-word structure",
        destroys="Word order, cross-word patterns"
    )

    # Diagnostic nulls for length-scale
    for k in [1, 2, 4, 8, 16, 32, 64, 128]:
        register_null(
            f"block_{k}",
            lambda t, rng, k=k: null_block_shuffle_letters(t, k, rng),
            NullType.TEXT,
            preserves=f"Patterns within {k}-letter blocks",
            destroys=f"Patterns across {k}-letter blocks"
        )

    # Random shuffle (baseline)
    register_null(
        "random",
        null_random_shuffle_bits,
        NullType.BITS,
        preserves="0/1 ratio only",
        destroys="All sequential structure"
    )

    # Metrics - multiple compressors required
    register_metric("zlib", metric_compression_zlib, MetricDirection.LOWER, "zlib compression ratio")
    register_metric("bz2", metric_compression_bz2, MetricDirection.LOWER, "bz2 compression ratio")
    register_metric("lzma", metric_compression_lzma, MetricDirection.LOWER, "lzma compression ratio")


_init_builtins()


# ============================================================
# TEST SPECIFICATION
# ============================================================

@dataclass(frozen=True)
class TestSpec:
    """
    Complete test specification. Frozen = can't change after creation.

    Everything needed to reproduce a test.
    """
    corpus: str
    encoding: str
    null: str
    metric: str
    n_perm: int = 1000
    seed: int = 42

    def validate(self) -> List[str]:
        """
        Validate all components are registered.

        Returns list of errors (empty = valid).
        """
        errors = []
        if self.corpus not in CORPORA:
            errors.append(f"Corpus '{self.corpus}' not registered")
        if self.encoding not in ENCODINGS:
            errors.append(f"Encoding '{self.encoding}' not registered")
        if self.null not in NULLS:
            errors.append(f"Null model '{self.null}' not registered")
        if self.metric not in METRICS:
            errors.append(f"Metric '{self.metric}' not registered")
        if self.n_perm < 100:
            errors.append("n_perm must be >= 100 for meaningful p-value")
        return errors


@dataclass
class TestResult:
    """Result of a single test."""
    spec: TestSpec
    observed: float
    null_distribution: List[float]
    p_value: float
    effect_bits_per_char: float

    @property
    def null_mean(self) -> float:
        return sum(self.null_distribution) / len(self.null_distribution)

    @property
    def null_std(self) -> float:
        mean = self.null_mean
        return (sum((x - mean)**2 for x in self.null_distribution) / len(self.null_distribution)) ** 0.5

    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha

    def summary(self) -> str:
        return (
            f"p={self.p_value:.4f}, "
            f"effect={self.effect_bits_per_char:.4f} bits/char, "
            f"observed={self.observed:.4f}, "
            f"null={self.null_mean:.4f}±{self.null_std:.4f}"
        )


# ============================================================
# TEST EXECUTION
# ============================================================

def run_test(spec: TestSpec) -> TestResult:
    """
    Execute a validated test specification.

    This is THE entry point. No escape from validation.
    """
    # Validate first
    errors = spec.validate()
    if errors:
        raise ValueError(f"Invalid TestSpec: {'; '.join(errors)}")

    # Get components
    corpus = CORPORA[spec.corpus]
    encoding = ENCODINGS[spec.encoding]
    null = NULLS[spec.null]
    metric = METRICS[spec.metric]

    rng = random.Random(spec.seed)

    # Encode original text
    bits = encoding.fn(corpus.text)
    if not bits:
        raise ValueError(f"Encoding {spec.encoding} produced empty bitstring")

    # Compute observed metric
    observed = metric.fn(bits)

    # Generate null distribution
    null_distribution = []

    for _ in range(spec.n_perm):
        if null.null_type == NullType.TEXT:
            # Null operates on text, then encode
            null_text = null.fn(corpus.text, rng)
            null_bits = encoding.fn(null_text)
        else:
            # Null operates on bits directly
            null_bits = null.fn(bits, rng)

        null_distribution.append(metric.fn(null_bits))

    # Compute p-value
    if metric.direction == MetricDirection.LOWER:
        # Lower = more structure, count how many nulls are as extreme
        count_extreme = sum(1 for x in null_distribution if x <= observed)
    else:
        # Higher = more structure
        count_extreme = sum(1 for x in null_distribution if x >= observed)

    p_value = (count_extreme + 1) / (spec.n_perm + 1)

    # Effect size in bits/char
    null_mean = sum(null_distribution) / len(null_distribution)
    effect_bits_per_char = (null_mean - observed) * 8  # CR difference * 8 bits/byte

    return TestResult(
        spec=spec,
        observed=observed,
        null_distribution=null_distribution,
        p_value=p_value,
        effect_bits_per_char=effect_bits_per_char
    )


# ============================================================
# LENGTH-SCALE DIAGNOSTIC
# ============================================================

@dataclass(frozen=True)
class LengthScaleSpec:
    """Specification for length-scale diagnostic."""
    corpus: str
    encoding: str
    metric: str
    block_sizes: Tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128)
    n_perm: int = 1000
    seed: int = 42

    def validate(self) -> List[str]:
        errors = []
        if self.corpus not in CORPORA:
            errors.append(f"Corpus '{self.corpus}' not registered")
        if self.encoding not in ENCODINGS:
            errors.append(f"Encoding '{self.encoding}' not registered")
        if self.metric not in METRICS:
            errors.append(f"Metric '{self.metric}' not registered")
        return errors


@dataclass
class LengthScaleResult:
    """Result of length-scale diagnostic."""
    spec: LengthScaleSpec
    curve: List[Tuple[int, float, float]]  # (block_size, effect_bits/char, p_value)

    def vanishes_at(self, threshold: float = 0.01) -> Optional[int]:
        """
        At what block size does the effect vanish?

        Returns None if effect persists at all scales.
        """
        for block_size, effect, p in self.curve:
            if abs(effect) < threshold or p > 0.05:
                return block_size
        return None

    def interpretation(self) -> str:
        """Human-readable interpretation."""
        vanish = self.vanishes_at()
        if vanish is None:
            return "LONG-RANGE: Structure persists at all tested scales"
        elif vanish <= 2:
            return "LETTER-LOCAL: Structure is within adjacent letters only"
        elif vanish <= 8:
            return f"WORD-SCALE: Structure vanishes at ~{vanish} letters"
        elif vanish <= 32:
            return f"PHRASE-SCALE: Structure vanishes at ~{vanish} letters"
        else:
            return f"SENTENCE-SCALE: Structure vanishes at ~{vanish} letters"

    def summary_table(self) -> str:
        """Format results as table."""
        lines = ["Block Size | Effect (bits/char) | p-value"]
        lines.append("-" * 45)
        for block_size, effect, p in self.curve:
            sig = "*" if p < 0.05 else ""
            lines.append(f"{block_size:10d} | {effect:18.4f} | {p:.4f}{sig}")
        lines.append("")
        lines.append(f"Interpretation: {self.interpretation()}")
        return "\n".join(lines)


def run_length_scale_test(spec: LengthScaleSpec) -> LengthScaleResult:
    """
    Run length-scale diagnostic.

    Shows at what scale structure vanishes → reveals if structure
    is letter-local, word-scale, phrase-scale, or long-range.
    """
    errors = spec.validate()
    if errors:
        raise ValueError(f"Invalid LengthScaleSpec: {'; '.join(errors)}")

    curve = []

    for block_size in spec.block_sizes:
        null_name = f"block_{block_size}"

        # Ensure null exists
        if null_name not in NULLS:
            register_null(
                null_name,
                lambda t, rng, k=block_size: null_block_shuffle_letters(t, k, rng),
                NullType.TEXT,
                preserves=f"Patterns within {block_size}-letter blocks",
                destroys=f"Patterns across {block_size}-letter blocks"
            )

        test_spec = TestSpec(
            corpus=spec.corpus,
            encoding=spec.encoding,
            null=null_name,
            metric=spec.metric,
            n_perm=spec.n_perm,
            seed=spec.seed + block_size  # Different seed per block size
        )

        result = run_test(test_spec)
        curve.append((block_size, result.effect_bits_per_char, result.p_value))

    return LengthScaleResult(spec=spec, curve=curve)


# ============================================================
# MULTI-COMPRESSOR ROBUSTNESS TEST
# ============================================================

@dataclass
class RobustnessResult:
    """Result of multi-compressor robustness test."""
    encoding: str
    null: str
    corpus: str
    results: Dict[str, TestResult]  # metric_name -> result

    def is_robust(self, alpha: float = 0.05) -> bool:
        """True if significant across ALL compressors."""
        return all(r.is_significant(alpha) for r in self.results.values())

    def summary(self) -> str:
        lines = [f"Robustness test: {self.encoding} vs {self.null} on {self.corpus}"]
        lines.append("-" * 60)
        for metric, result in self.results.items():
            sig = "SIG" if result.is_significant() else "NS"
            lines.append(f"  {metric}: p={result.p_value:.4f}, effect={result.effect_bits_per_char:.4f} [{sig}]")
        lines.append("-" * 60)
        lines.append(f"ROBUST: {self.is_robust()}")
        return "\n".join(lines)


def run_robustness_test(
    corpus: str,
    encoding: str,
    null: str = "word_perm",
    n_perm: int = 1000,
    seed: int = 42
) -> RobustnessResult:
    """
    Test encoding with all compressors.

    If effect only appears with one compressor → compressor quirk, not real structure.
    """
    results = {}

    for metric_name in ["zlib", "bz2", "lzma"]:
        spec = TestSpec(
            corpus=corpus,
            encoding=encoding,
            null=null,
            metric=metric_name,
            n_perm=n_perm,
            seed=seed
        )
        results[metric_name] = run_test(spec)

    return RobustnessResult(
        encoding=encoding,
        null=null,
        corpus=corpus,
        results=results
    )


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def list_registered() -> Dict[str, List[str]]:
    """List all registered components."""
    return {
        "encodings": list(ENCODINGS.keys()),
        "nulls": list(NULLS.keys()),
        "metrics": list(METRICS.keys()),
        "corpora": list(CORPORA.keys())
    }


def quick_test(
    corpus: str,
    encoding: str,
    n_perm: int = 1000
) -> Dict[str, Any]:
    """
    Quick test with critical null (word_perm) and all compressors.

    This is the minimum bar for any claim about cross-word structure.
    """
    robustness = run_robustness_test(corpus, encoding, "word_perm", n_perm)

    return {
        "encoding": encoding,
        "corpus": corpus,
        "null": "word_perm",
        "robust": robustness.is_robust(),
        "results": {
            name: {
                "p_value": r.p_value,
                "effect_bits_per_char": r.effect_bits_per_char,
                "significant": r.is_significant()
            }
            for name, r in robustness.results.items()
        },
        "interpretation": (
            "REAL STRUCTURE: Beats word permutation robustly across compressors"
            if robustness.is_robust()
            else "NO CLAIM: Does not robustly beat word permutation"
        )
    }

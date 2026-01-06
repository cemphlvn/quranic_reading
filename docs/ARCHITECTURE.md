# System Architecture

Self-validating research infrastructure. All tests MUST go through the API.

---

## Core Question

```
Does encoding show structure BEYOND word boundaries?
```

---

## Design Principles

1. **No escape from methodology**: All tests go through `run_test()`
2. **Registry validation**: Components validated at registration AND at test time
3. **Word permutation is critical null**: Keeps words, shuffles order
4. **Multi-compressor robustness**: Must pass zlib, bz2, AND lzma
5. **Length-scale diagnostic**: Block-shuffle curve reveals structure scale

---

## Directory Structure

```
quranic_reading/
├── data/quran/quran.json     # Immutable source text
├── docs/
│   ├── METHODOLOGY.md        # What we're testing, what nulls mean
│   ├── FINDINGS.md           # Honest assessment of results
│   └── ARCHITECTURE.md       # This file
├── src/
│   ├── core/
│   │   ├── api.py            # THE CORE - all tests go here
│   │   ├── binary_analysis.py # Text loading, basic analysis
│   │   └── __init__.py       # Exports
│   └── encoding_functions/   # Letter → {0,1} mappings
├── .claude/commands/
│   ├── register.md           # /register
│   ├── test.md               # /test
│   └── length-scale.md       # /length-scale
└── logs/                     # Research traces
```

---

## API Overview

### Registration (before testing)

```python
from core import register_encoding, register_corpus, load_quran_corpus

# Load Quran corpus
load_quran_corpus()

# Register encoding
register_encoding(
    name="E_dot",
    fn=lambda text: ''.join('1' if has_dot(c) else '0' for c in text),
    description="Dotted vs undotted",
    hypothesis="Dots carry semantic load",
    preregistered=True
)
```

### Testing

```python
from core import quick_test, run_length_scale_test, LengthScaleSpec

# Quick test against word permutation (the critical null)
result = quick_test(corpus="quran", encoding="E_dot", n_perm=1000)
print(result["interpretation"])

# Length-scale diagnostic
spec = LengthScaleSpec(corpus="quran", encoding="E_dot", metric="zlib")
curve = run_length_scale_test(spec)
print(curve.summary_table())
```

---

## Null Model Hierarchy

| Null | Preserves | Destroys | Use For |
|------|-----------|----------|---------|
| **word_perm** | Words intact | Word order | Cross-word structure |
| block_k | k-letter patterns | Longer patterns | Length-scale diagnostic |
| random | 0/1 ratio | Everything | Baseline (trivial) |

**Critical**: Claims require beating `word_perm` robustly across compressors.

---

## Testing Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        TestSpec                              │
│  corpus + encoding + null + metric + n_perm + seed          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      VALIDATION                              │
│  All components must be registered, n_perm >= 100           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     run_test(spec)                          │
│  • Encode text → bits                                       │
│  • Generate null distribution (n_perm times)                │
│  • Compute p-value: (count_extreme + 1) / (n_perm + 1)     │
│  • Compute effect size: bits/char                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      TestResult                              │
│  observed, null_distribution, p_value, effect_bits/char    │
└─────────────────────────────────────────────────────────────┘
```

---

## Claim Levels

| Level | Requirement | Status |
|-------|-------------|--------|
| L0 | Beats random shuffle | Trivial |
| L1 | Beats word_perm with zlib | NOT TESTED |
| L2 | Robust across all compressors | NOT TESTED |
| L3 | Effect > 0.01 bits/char | NOT TESTED |
| L4 | Length-scale > WORD-SCALE | NOT TESTED |
| L5 | Unique to Quran (cross-corpus) | NOT TESTED |

**No claim valid below L2 + L3.**

---

## Effect Size Interpretation

```
Δ < 0.001 bits/char : Trivially small, ignore
Δ 0.001-0.01        : Small, needs investigation
Δ 0.01-0.1          : Moderate, potentially interesting
Δ > 0.1             : Large, worth pursuing
```

---

## Length-Scale Interpretation

| Result | Meaning |
|--------|---------|
| LETTER-LOCAL | Structure within 1-2 letters (trivial) |
| WORD-SCALE | Within-word structure (expected) |
| PHRASE-SCALE | Cross-word, 2-4 words (interesting) |
| SENTENCE-SCALE | Multi-phrase structure (very interesting) |
| LONG-RANGE | Persists at all scales (investigate) |

---

## Commands

```
/register encoding <name> <desc>  # Register new encoding
/test <encoding>                  # Test against word_perm
/length-scale <encoding>          # Run length-scale diagnostic
```

---

## Adding New Encodings

1. Define function in `src/encoding_functions/`
2. Write hypothesis BEFORE testing (pre-registration)
3. Register via API
4. Run: `/test <name>`
5. Only claim if: beats word_perm robustly + effect > 0.01

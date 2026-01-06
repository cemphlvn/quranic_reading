# Quranic Reading: Binary Encoding Analysis

Testing whether binary encodings show structure beyond word boundaries.

## Core Question

```
Does encoding show cross-word structure?
```

## Honest Status

| Question | Answer | Evidence |
|----------|--------|----------|
| Beats random shuffle? | Yes | Trivial (any text does) |
| Beats word permutation? | **NOT TESTED** | Critical null |
| Robust across compressors? | **NOT TESTED** | Must pass all 3 |
| Structure scale? | **NOT TESTED** | Need length-scale test |
| Unique to Quran? | **NOT TESTED** | No cross-corpus |

**Bottom line**: We have compression signal. We don't know if it's meaningful.

---

## Commands

```
/register encoding <name> <desc>  # Add new encoding
/test <encoding>                  # Test vs word permutation
/length-scale <encoding>          # Diagnose structure scale
```

---

## Quick Start

```python
import sys; sys.path.insert(0, 'src')
from core import load_quran_corpus, register_encoding, quick_test

# Load corpus
load_quran_corpus()

# Register encoding
DOTTED = set('بتثجخذزشضظغفقنيء')
register_encoding(
    name="E_dot",
    fn=lambda t: ''.join('1' if c in DOTTED else '0' for c in t if '\u0621' <= c <= '\u064A'),
    description="Dotted letters = 1",
    hypothesis="Dots correlate with semantic density",
    preregistered=True
)

# Test
result = quick_test("quran", "E_dot", n_perm=1000)
print(result["interpretation"])
```

---

## What Would Make This Science

1. **Beat word permutation robustly** - structure beyond word order
2. **All 3 compressors** - not a zlib quirk
3. **Effect > 0.01 bits/char** - not trivially small
4. **Length-scale > WORD-SCALE** - structure spans words
5. **Cross-corpus comparison** - unique to Quran

---

## Null Models

| Null | What It Tests |
|------|---------------|
| **word_perm** | Cross-word structure (critical) |
| block_k | Structure at k-letter scale |
| random | Any structure at all (trivial) |

---

## Effect Size Guide

```
< 0.001 bits/char : Trivial, ignore
0.001-0.01        : Small, investigate
0.01-0.1          : Moderate, interesting
> 0.1             : Large, pursue
```

---

## File Structure

```
quranic_reading/
├── src/core/api.py       # THE CORE - all tests here
├── src/encoding_functions/
├── docs/ARCHITECTURE.md  # Full system design
├── .claude/commands/     # /register, /test, /length-scale
└── data/quran/
```

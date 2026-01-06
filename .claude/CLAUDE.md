# Quranic Reading Research

Binary encoding analysis with self-validating methodology.

## Core Question

```
Does encoding show structure BEYOND word boundaries?
```

## Commands

| Command | Purpose |
|---------|---------|
| `/status` | Show registered components |
| `/register <type> <name> <desc>` | Register encoding or corpus |
| `/test <encoding>` | Test vs word permutation null |
| `/length-scale <encoding>` | Diagnose structure scale |

## Quick Start

```python
# In any test
import sys; sys.path.insert(0, 'src')
from core import load_quran_corpus, register_encoding, quick_test

load_quran_corpus()
# register encoding...
result = quick_test("quran", "encoding_name", n_perm=1000)
```

## Architecture

All tests go through `src/core/api.py`. No escape from methodology.

```
TestSpec → validate() → run_test() → TestResult
```

Key constraints:
- n_perm >= 100 enforced
- Must beat word_perm null (critical)
- Must pass all 3 compressors (robustness)
- Effect > 0.01 bits/char (meaningful)

## Docs

| File | Content |
|------|---------|
| `docs/ARCHITECTURE.md` | System design |
| `docs/METHODOLOGY.md` | What we test, what nulls mean |
| `docs/FINDINGS.md` | Honest results |
| `docs/AXIOMS.md` | Minimal assumptions |

## Claim Levels

| Level | Requirement |
|-------|-------------|
| L0 | Beats random shuffle (trivial) |
| L1 | Beats word_perm |
| L2 | Robust across zlib/bz2/lzma |
| L3 | Effect > 0.01 bits/char |
| L4 | Scale > WORD-SCALE |
| L5 | Cross-corpus validated |

**No claim valid below L2 + L3.**

## Principles

1. **No escape** - All tests through API
2. **Validation first** - Components checked at test time
3. **Multiple compressors** - Not just zlib
4. **Effect size** - p-value alone insufficient
5. **Pre-registration** - Hypothesis before results

---
description: Test encoding against word permutation null
argument-hint: <encoding_name>
allowed-tools: Read, Bash(python3:*)
---

# Test Encoding

Test encoding `$1` against the critical null (word permutation) with all compressors.

## Task

Run this test:

```python
import sys; sys.path.insert(0, 'src')
from core import load_quran_corpus, quick_test

# Ensure corpus loaded
load_quran_corpus()

# Import and register the encoding
from encoding_functions.$1 import *

# Run test
result = quick_test(corpus="quran", encoding="$1", n_perm=1000)

# Report
print(f"\nTesting $1 vs word_perm on quran")
print("-" * 50)
for metric, r in result["results"].items():
    sig = "SIG" if r["significant"] else "NS"
    print(f"  {metric}: p={r['p_value']:.4f}, effect={r['effect_bits_per_char']:.4f} [{sig}]")
print("-" * 50)
print(f"ROBUST: {result['robust']}")
print(f"\n{result['interpretation']}")
```

## Interpretation Guide

| Result | Meaning |
|--------|---------|
| ROBUST + SIG all | Real cross-word structure |
| Mixed SIG | Questionable - investigate |
| No SIG | No evidence for structure |

## Effect Sizes

```
< 0.001 : Trivial
0.001-0.01 : Small
0.01-0.1 : Moderate
> 0.1 : Large
```

## Requirements

- Encoding `$1` must be registered
- Quran corpus auto-loads
- n_perm=1000 for valid p-values

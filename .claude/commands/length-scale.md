---
description: Diagnose structure scale of an encoding
argument-hint: <encoding_name>
allowed-tools: Read, Bash(python3:*)
---

# Length-Scale Diagnostic

Reveal at what scale structure exists in encoding `$1`.

## Task

Run this diagnostic:

```python
import sys; sys.path.insert(0, 'src')
from core import load_quran_corpus, LengthScaleSpec, run_length_scale_test

# Load corpus
load_quran_corpus()

# Import encoding
from encoding_functions.$1 import *

# Run length-scale test
spec = LengthScaleSpec(
    corpus="quran",
    encoding="$1",
    metric="zlib",
    block_sizes=(1, 2, 4, 8, 16, 32, 64, 128),
    n_perm=500  # Faster for diagnostic
)

result = run_length_scale_test(spec)
print(result.summary_table())
```

## Interpretation

| Scale | Meaning | Significance |
|-------|---------|--------------|
| LETTER-LOCAL (1-2) | Adjacent letter patterns | Trivial (digrams) |
| WORD-SCALE (4-8) | Within-word structure | Expected (morphology) |
| PHRASE-SCALE (16-32) | Cross-word patterns | Interesting |
| SENTENCE-SCALE (64+) | Long-range structure | Very interesting |
| LONG-RANGE | Persists all scales | Investigate |

## What It Tests

Block shuffle at sizes 1, 2, 4, 8, 16, 32, 64, 128 letters.

At each size k:
- Shuffle k-letter blocks within words
- Measure if structure remains

When effect vanishes → that's the structure's scale.

## Requirements

- Encoding `$1` must be registered
- Takes ~5-10 min with n_perm=500

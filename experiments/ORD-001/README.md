# ORD-001: Ordinal Encoding Experiments

**Status:** COMPLETE
**Date:** January 2026

## Question

Do letter-position encodings show cross-word structure?

## Hypothesis

- **Negative controls** (parity, high/low): Expect NO structure
- **Exploratory** (5-bit, delta): Unknown

## Encodings Tested

| Encoding | Description | Hypothesis |
|----------|-------------|------------|
| ord_parity_abjad | Even/Odd in Abjadi order | NEGATIVE CONTROL |
| ord_parity_hijai | Even/Odd in Hijai order | NEGATIVE CONTROL |
| ord_high_low_abjad | First/Second half | NEGATIVE CONTROL |
| ord_high_low_hijai | First/Second half | NEGATIVE CONTROL |
| ord_5bit_abjad | 5-bit binary ordinal | EXPLORATORY |
| ord_5bit_hijai | 5-bit binary ordinal | EXPLORATORY |
| ord_delta_sign | Rising/falling transitions | EXPLORATORY |

## Results

Unexpected: Even negative controls showed some structure (p=0.032).
5-bit ordinal showed strongest effect (0.10 bits/char).

**Interpretation:** This may reflect Arabic phonotactics or morphological constraints, not hidden numerical codes.

## Files

```
src/
  analysis.py       # Main experiment
  encodings.py      # Ordinal encoding functions
```

## Run

```bash
cd experiments/ORD-001
python src/analysis.py --n_perm 1000
```

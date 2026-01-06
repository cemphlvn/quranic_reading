# Methodology

Statistical framework for binary encoding analysis.

---

## What We Are Actually Testing

```
H₀: Binary encodings of Quranic text are no more compressible
    than appropriate null models.

H₁: Binary encodings show excess compressibility beyond what
    null models predict.
```

**Critical distinction:**
- "Excess compressibility" ≠ "meaningful structure"
- "Beats null" ≠ "unique to Quran"
- "Statistical significance" ≠ "semantic interpretation"

---

## The Compression Problem

Compression detects **predictability**, not **meaning**.

Compressors will report "structure" for:
- Imbalanced 0/1 ratio
- Long runs of same bit
- Repeated local patterns
- Consistent alternations

These are often **boring artifacts** of:
- Arabic orthography
- Letter frequency distributions
- Morphological constraints
- How compressors handle binary strings

---

## Required Null Models (Hierarchy)

Each null isolates a different factor:

### N1: Random Shuffle (weakest)
```
Method: Shuffle all bits randomly
Preserves: Nothing (0/1 ratio only)
Destroys: Everything
Problem: Too easy to beat
```

### N2: Bit-Preserving Shuffle
```
Method: Shuffle bits, preserve overall 1-rate
Preserves: Global density
Destroys: All sequential structure
```

### N3: Block Shuffle
```
Method: Shuffle chunks of k bits (k=10-50)
Preserves: Local patterns within blocks
Destroys: Long-range structure
Tests: Is structure local or global?
```

### N4: Markov Surrogate (critical)
```
Method: Generate new bitstring with same:
  - 1-rate
  - Transition probs P(1|0), P(1|1)
Preserves: First-order sequential statistics
Destroys: Higher-order structure
Tests: Is structure beyond Markov?
```

### N5: Word Permutation (critical for "beyond word" claims)
```
Method: Keep each word's encoding intact, shuffle word ORDER
Preserves: Within-word structure
Destroys: Cross-word structure
Tests: Is structure truly beyond word boundaries?
```

### N6: Cross-Corpus Comparison (required for uniqueness claims)
```
Method: Apply same encoding to other Arabic texts
Compares: Quran vs pre-Islamic poetry, prose, Hadith
Tests: Is structure Quran-specific or Arabic-general?
```

---

## Statistical Requirements

### Permutation P-Value (not z-score)

```python
p = (count(null >= observed) + 1) / (N + 1)
```

- Minimum N = 1,000 for stable estimates
- N = 10,000 for tail precision
- Report exact permutation p, not normal approximation

### Effect Size (required)

```
Δ_bits = (CR_null - CR_observed) * len(bitstring) * 8

Interpretation:
  Δ < 100 bits total: trivially small
  Δ < 0.01 bits/char: probably artifact
  Δ > 0.1 bits/char: potentially meaningful
```

### Compressor Robustness

Test with multiple compressors:
- zlib (default)
- gzip
- bzip2
- lzma
- zstd

If effect only appears with one compressor → compressor quirk, not structure.

### Multiple Comparison Correction

```
k = number of encodings
α_adjusted = α / k  (Bonferroni)

For k=16: α = 0.003125
```

---

## Claim Hierarchy (Keep Separated)

### Level 1: Statistical Finding
```
"E8_solar encoding produces bitstrings that compress
 X bits/char better than Markov surrogate baseline."
```
This is what we can measure.

### Level 2: Linguistic Hypothesis
```
"This excess compressibility reflects phonotactic or
 morphological constraints in Classical Arabic."
```
This requires cross-corpus comparison.

### Level 3: Uniqueness Claim
```
"This structure is unique to the Quran, not general Arabic."
```
This requires Quran vs other-Arabic comparison.

### Level 4: Semantic Interpretation
```
"Solar letters encode 'manifest' concepts."
```
This is post-hoc speculation until validated.

---

## Current Status

| Requirement | Status |
|-------------|--------|
| Random shuffle null | ✓ Implemented |
| Markov surrogate | ✗ NOT DONE |
| Word permutation null | ✗ NOT DONE |
| Block shuffle | ✗ NOT DONE |
| Multiple compressors | ✗ NOT DONE |
| Permutation p-value | ✗ NOT DONE |
| Effect size (bits/char) | ✗ NOT DONE |
| Cross-corpus baseline | ✗ NOT DONE |
| Verse length normalization | ✗ NOT DONE |

---

## What We Have Actually Shown

1. Binary encodings of Quran text compress better than random shuffle
2. This is expected for ANY natural language text
3. We cannot yet distinguish Quran-specific from Arabic-general
4. All semantic interpretations are post-hoc speculation

---

## What Would Convince a Hostile Reviewer

1. **Cross-corpus test**: Quran vs pre-Islamic poetry, Hadith, prose
2. **Compressor robustness**: Same effect across gzip, bzip2, lzma, zstd
3. **Proper nulls**: Markov surrogate, word permutation, block shuffle
4. **Pre-registration**: Freeze encodings, test on held-out data
5. **Mechanistic explanation**: Why does this encoding create structure?

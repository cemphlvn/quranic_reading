# Quranic Structure Analysis

> Computational detection of structural patterns in the Quran using binary encodings, compression analysis, and rigorous statistical methods.

---

## About This Project

This project applies information theory and statistical methods to test whether the Quran contains structural patterns beyond ordinary language. We use **compression as a structure detector**: patterns allow better compression, so comparing compression ratios against null models reveals hidden structure.

**Core Principle:** Every claim must be validated against proper null models. We report both positive and negative results honestly.

---

## Main Finding

### The Muqattaat Function as Section Markers

[![Similarity Analysis](experiments/MUQ-001/output/figures/fig1_similarity.png)](experiments/MUQ-001/output/paper.html)
*Click to view full paper*

Twenty-nine Quranic surahs begin with mysterious letter combinations called *muqattaat* (e.g., الم, حم, الر). Their meaning has puzzled scholars for 1400 years.

**Our Discovery:** Surahs sharing the same muqattaat code are **~2x more thematically similar** than random groups.

| Code | Arabic | Surahs | Effect | P-value |
|------|--------|--------|--------|---------|
| Ha-Mim | حم | 40-46 (consecutive) | **+83%** | 0.002 |
| Alif-Lam-Ra | الر | 10, 11, 12, 14, 15 | **+98%** | 0.002 |
| Alif-Lam-Mim | الم | 2, 3, 29, 30, 31, 32 | **+94%** | 0.002 |
| Ta-Sin | طس | 26, 27, 28 | **+94%** | 0.020 |

**Conclusion:** The muqattaat likely function as an **ancient table of contents**—section markers grouping thematically related surahs.

### [Read Full Paper with Visualizations →](experiments/MUQ-001/output/paper.html)

---

## All Experiments

| ID | Experiment | Hypothesis | Result | Status |
|----|-----------|------------|--------|--------|
| [MUQ-001](experiments/MUQ-001/) | Muqattaat Themes | Same-code surahs share themes | **CONFIRMED** (p<0.002) | Complete |
| [STR-001](experiments/STR-001/) | Structure Localization | Find where structure exists | Mixed: 51% cross-verse | Complete |
| [ORD-001](experiments/ORD-001/) | Ordinal Encoding | Letter-order has structure | Weak signal found | Complete |

---

## Results Summary

### Positive Results (Validated)

| Finding | Evidence | Confidence |
|---------|----------|------------|
| Muqattaat mark thematic sections | 2x similarity, p<0.002 | **High** |
| Cross-word structure exists | Beats word permutation | **High** |
| Surahs with refrains show structure | Ar-Rahman, Ash-Shu'ara top | **High** |

### Negative Results (Null Not Rejected)

| Hypothesis | Outcome | Interpretation |
|------------|---------|----------------|
| Gematria codes | No significant pattern | Code 19 claims unsupported |
| Letter parity patterns | Expected null behavior | Confirms methodology works |
| Ordinal high/low split | Expected null behavior | Arbitrary splits show nothing |

### Inconclusive / Needs More Work

| Question | Current Status |
|----------|----------------|
| Why Medinan > Meccan structure? | Observed but unexplained |
| Isolated muqattaat meaning? | Only grouped codes tested |
| Cross-corpus uniqueness | Not yet tested |

---

## Methodology

### The Core Question

```
Does encoding X reveal structure BEYOND word boundaries?
```

### Null Model: Word Permutation

We shuffle **word order** while keeping words intact. If an encoding compresses the original better than shuffled versions, it detected **cross-word structure**.

```
Original:  "In the name of God the merciful the compassionate"
Shuffled:  "compassionate God the In merciful of the name the"
                       ↓
         Same words, destroyed cross-word patterns
```

### Validation Levels

| Level | Requirement | Meaning |
|-------|-------------|---------|
| L0 | Beats random shuffle | Trivial (any text does this) |
| L1 | Beats word permutation | Cross-word structure exists |
| **L2** | **All 3 compressors** | **Not a compression quirk** |
| **L3** | **Effect > 0.01 bits/char** | **Meaningful magnitude** |
| L4 | Scale > word length | Structure spans phrases |
| L5 | Cross-corpus unique | Specific to this text |

**No claim valid below L2 + L3.**

---

## What This Is NOT

| This Project | NOT This |
|-------------|----------|
| Statistical pattern detection | Hidden code discovery |
| Null-model validated | Cherry-picked coincidences |
| Reports negative results | Confirmation bias |
| Compression-based | Gematria / numerology |
| Reproducible code | Subjective interpretation |

---

## Project Structure

```
quranic_reading/
├── experiments/                 # Each experiment isolated
│   ├── MUQ-001/                # Muqattaat theme analysis
│   │   ├── README.md           # Hypothesis, method, results
│   │   ├── src/                # Analysis scripts
│   │   └── output/             # Results, figures, paper
│   ├── STR-001/                # Structure localization
│   └── ORD-001/                # Ordinal encoding tests
├── src/
│   ├── core/                   # Framework (API, stats, nulls)
│   └── encoding_functions/     # Shared encoding implementations
├── data/
│   └── quran/                  # Source corpus (Tanzil Uthmani)
├── EXPERIMENTS.md              # Experiment registry & conventions
└── README.md                   # This file
```

---

## Quick Start

```bash
# Clone and setup
git clone [repo] && cd quranic_reading
python -m venv .venv && source .venv/bin/activate
pip install matplotlib numpy

# Run main finding
python experiments/MUQ-001/src/analysis.py

# Generate visualizations
python experiments/MUQ-001/src/visualize.py

# View results
open experiments/MUQ-001/output/paper.html
```

---

## Technical Details

### Compression as Structure Detector

Information theory: **compression ratio measures predictability**. If knowing earlier parts helps predict later parts, compression improves. Cross-word structure means words aren't independent—there's pattern spanning word boundaries.

### Effect Size Interpretation

```
< 0.001 bits/char : Trivial, ignore
0.001 - 0.01      : Small, investigate
0.01 - 0.1        : Moderate, interesting
> 0.1             : Large, pursue
```

### Compressors Used

- **zlib** (DEFLATE) - General purpose
- **bz2** (Burrows-Wheeler) - Different algorithm
- **lzma** (Lempel-Ziv-Markov) - High compression

Results must hold across all three to rule out algorithm-specific artifacts.

---

## Contributing

New experiments should:

1. Create folder: `experiments/XXX-NNN/`
2. Include `README.md` with hypothesis, method, results
3. Use proper null models (see `src/core/null_models.py`)
4. Report effect sizes, not just p-values
5. Register in `EXPERIMENTS.md`

---

## Citation

```bibtex
@misc{quranic_structure_2026,
  title={Quranic Structure Analysis: Computational Evidence for Muqattaat as Section Markers},
  year={2026},
  url={https://github.com/[repo]}
}
```

---

## License

Research code provided for academic use. Quran text from [Tanzil.net](https://tanzil.net/) (Uthmani script).

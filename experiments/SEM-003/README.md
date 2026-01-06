# SEM-003: Semantic Sentiment Axes

**Status:** ARCHIVED (INVALID)
**Date:** January 2026
**Result:** METHODOLOGY FLAW - synthetic pole phrases not orthogonal in embedding space

## Why This Failed

Rigor check revealed that pole centroids are too similar:
- certainty ↔ contention: 0.745 (should be ~0, they're "opposites")
- threat ↔ contention: 0.702 (cross-axis contamination)

The -0.79 correlation between axes was an **artifact** of overlapping pole definitions, not a real rhetorical pattern. The embedding model clusters all "religious discourse about truth" together regardless of our intended semantic distinctions.

**Lesson:** Synthetic pole phrases don't guarantee orthogonal axes. Need data-driven approach (PCA) or validated exemplar ayahs.

## Objective

Project each ayah onto interpretable semantic axes to reveal the **rhetorical structure** of the Quran. Unlike topic clustering, these axes capture meaning gradients.

## The Six Axes

| Axis | Negative Pole | Positive Pole | What It Captures |
|------|---------------|---------------|------------------|
| **1. Threat ↔ Mercy** | Punishment, Hell, destruction | Forgiveness, guidance, paradise | Warning–Reassurance oscillation |
| **2. Narrative ↔ Normative** | Stories, prophets, past tense | Commands, laws, ethics | Discourse mode |
| **3. Immanence ↔ Transcendence** | Earth, provision, worldly | Afterlife, angels, unseen | Grounding vs lifting |
| **4. Intimacy ↔ Majesty** | Direct address, 2nd person | Cosmic scale, 3rd person | Rhetorical distance |
| **5. Certainty ↔ Contention** | Declarative facts | Polemics, refutations | Argumentative stance |
| **6. Hope ↔ Fear** | Promise, patience, reward | Urgency, warning | Motivational polarity |

## Method

### Axis Projection

For each axis with poles (P-, P+):

1. **Define anchor pools**: Ayahs strongly exemplifying each pole
2. **Compute centroids**: C- = mean(embeddings of P- ayahs), C+ = mean(embeddings of P+ ayahs)
3. **Project**: `score_i = cos(ayah_i, C+) - cos(ayah_i, C-)`

Result: signed scalar per ayah. Positive = toward P+, negative = toward P-.

### Anchor Selection

Anchors selected by **keyword presence** (Arabic terms):

| Axis | P- Keywords | P+ Keywords |
|------|-------------|-------------|
| Threat/Mercy | عذاب، نار، جهنم، هلك | رحمة، مغفرة، جنة، هدى |
| Narrative/Normative | قال، قوم، أرسل، نبأ | أقيموا، حرم، أمر، فرض |
| Immanence/Transcendence | أرض، رزق، دنيا، تجارة | آخرة، ملائكة، عرش، غيب |
| Intimacy/Majesty | يا أيها، قل، أنت | السماوات، خلق، ملك |
| Certainty/Contention | إن، حق، آمن | يجادل، كذب، زعم |
| Hope/Fear | بشر، صبر، وعد | ساعة، بغتة، عاجل |

### Validation

- Anchors must be **disjoint** (no ayah in both poles)
- Minimum **20 anchors per pole** for stability
- **Sanity check**: known exemplar ayahs should score as expected

## Hypotheses

1. **Oscillation**: Threat/Mercy will show wave-like patterns
2. **Surah resets**: Axes reset at surah boundaries
3. **Muqattaat signatures**: Ha-Mim surahs lean transcendent
4. **Meccan/Medinan split**: Meccan more threat/narrative, Medinan more normative

## Dependencies

```bash
# Already installed
pip install numpy matplotlib sentence-transformers
```

## Run

```bash
python src/define_anchors.py    # Build anchor pools
python src/compute_axes.py      # Project all ayahs
python src/visualize.py         # Generate plots
```

## Files

```
src/
  compute_axes.py     # Axis projection (embeds pole phrases)
  visualize.py        # Flow visualizations
output/
  data/
    axis_scores.json  # Scores per ayah per axis
  figures/
    axis_*.png        # Individual axis flows
    combined_axes.png # All 6 axes stacked
    surah_axis_heatmap.png
```

## Results

### Axis Statistics

| Axis | Range | Mean | Std | Interpretation |
|------|-------|------|-----|----------------|
| Threat ↔ Mercy | [-0.33, 0.18] | -0.01 | 0.05 | Balanced oscillation |
| Narrative ↔ Normative | [-0.08, 0.21] | +0.08 | 0.04 | Normative-leaning |
| Immanence ↔ Transcendence | [-0.06, 0.27] | +0.12 | 0.05 | Strongly transcendent |
| Intimacy ↔ Majesty | [-0.36, 0.13] | -0.14 | 0.08 | Strongly intimate |
| Certainty ↔ Contention | [-0.16, 0.22] | +0.01 | 0.04 | Balanced |
| Hope ↔ Fear | [-0.15, 0.28] | +0.03 | 0.05 | Slight fear-lean |

### Key Correlations

| Pair | Correlation | Interpretation |
|------|-------------|----------------|
| Threat ↔ Certainty | **-0.79** | Threat passages doubt; mercy passages assert |
| Threat ↔ Hope/Fear | **-0.66** | Threat ≠ Fear (different constructs) |
| Narrative ↔ Intimacy | **-0.58** | Stories use intimate address |
| Immanence ↔ Narrative | **-0.49** | Worldly ↔ Story mode |

### Meccan vs Medinan

| Axis | Meccan | Medinan | Δ | Interpretation |
|------|--------|---------|---|----------------|
| Immanence ↔ Transcendence | +0.11 | **+0.15** | +0.04 | Medinan more transcendent |
| Hope ↔ Fear | **+0.04** | +0.01 | -0.03 | Meccan more fear-oriented |
| Others | ~ | ~ | <0.01 | No significant difference |

### Visual Findings

![Combined Axes](output/figures/combined_axes.png)

**Observations:**
1. **Intimacy dominates** - Quran consistently uses intimate address (يا أيها)
2. **Transcendence baseline** - Text stays in "beyond" register
3. **Threat/Mercy oscillation** - Clear rhetorical waves
4. **Fear increases** toward later (shorter) surahs

![Surah Heatmap](output/figures/surah_axis_heatmap.png)

### Hypothesis Outcomes

| # | Hypothesis | Result |
|---|------------|--------|
| 1 | Threat/Mercy oscillates | **CONFIRMED** - visible waves |
| 2 | Surah resets at boundaries | **PARTIAL** - some axes reset |
| 3 | Muqattaat signatures | **NEEDS ANALYSIS** |
| 4 | Meccan/Medinan split | **CONFIRMED** - transcendence/fear differ |

# MUQ-001: Muqattaat Theme Analysis

**Status:** COMPLETE
**Date:** January 2026

## Hypothesis

If the muqattaat (mysterious letters) function as section markers, surahs sharing the same code should exhibit greater thematic similarity than random surah groups.

## Method

1. Extract vocabulary from each surah (stopwords removed)
2. Compute cosine similarity between surah pairs
3. Compare within-group similarity to random groups (n=500)
4. Statistical significance via permutation test

## Key Results

| Code | Surahs | Similarity | vs Random | P-value |
|------|--------|------------|-----------|---------|
| Ha-Mim | 40-46 | 0.717 | +83% | 0.002 |
| Alif-Lam-Ra | 10-15 | 0.772 | +98% | 0.002 |
| Alif-Lam-Mim | 2,3,29-32 | 0.766 | +94% | 0.002 |
| Ta-Sin | 26-28 | 0.752 | +94% | 0.020 |

**All 4 groups show ~2x higher similarity than random (p < 0.05)**

## Conclusion

The muqattaat correlate with thematic content. Same-code surahs share distinctive vocabulary, supporting the hypothesis that these mysterious letters function as **section markers** - an ancient table of contents.

## Files

```
src/
  analysis.py       # Theme similarity analysis
  distinctive.py    # Distinctive vocabulary extraction
  visualize.py      # Figure generation
output/
  results.json      # Similarity statistics
  distinctive.json  # Per-group vocabulary
  paper.html        # Full paper with visualizations
  figures/          # PNG/SVG charts
```

## Run

```bash
cd experiments/MUQ-001
python src/analysis.py
python src/distinctive.py
python src/visualize.py
```

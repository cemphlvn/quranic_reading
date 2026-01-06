# SEM-005: Within-Surah Arc Analysis

**Status:** COMPLETE
**Date:** January 2026
**Result:** Meccan surahs more semantically varied; no ring composition detected

## Objective

Do surahs have internal structure (intro → body → conclusion)?
Normalize each surah to [0, 1] and track embedding-based metrics across positions.

## Method

1. Group ayahs by surah
2. Normalize position to [0, 1] within each surah
3. Compute per-position metrics:
   - **Novelty**: distance from previous ayah
   - **Centroid distance**: distance from surah centroid
   - **First similarity**: similarity to first ayah
   - **Last similarity**: similarity to last ayah
4. Aggregate into 10 bins across all surahs
5. Test bookend hypothesis (ring composition)

## Key Results

### Arc Profile (All Surahs)

| Position | 0.0 | 0.2 | 0.5 | 0.8 | 1.0 |
|----------|-----|-----|-----|-----|-----|
| Novelty  | 0.11 | 0.14 | 0.14 | 0.14 | 0.14 |
| Centroid Dist | 0.08 | 0.08 | 0.08 | 0.08 | 0.08 |

**Finding:** Novelty lower at start (opening formula effect), otherwise relatively flat.

### Bookend Analysis (Ring Composition)

| Metric | First-Last | Random Pair |
|--------|------------|-------------|
| Mean Similarity | 0.798 | 0.838 |
| Std | 0.149 | 0.094 |

**Ratio: 0.95x** - First and last ayahs are NOT more similar than random pairs.

**Conclusion:** No statistical support for ring composition hypothesis.

### Meccan vs Medinan Arc Shapes

| Position | Meccan | Medinan | Δ |
|----------|--------|---------|---|
| Start (0.0) | 0.115 | 0.091 | +0.024 |
| Middle (0.5) | 0.147 | 0.109 | +0.038 |
| End (0.9) | 0.145 | 0.109 | +0.036 |

**Finding:** Meccan surahs consistently more novel (varied) across all positions.

## Visualizations

- `arc_profile.png` - Four metrics across normalized position
- `meccan_medinan_arcs.png` - Novelty comparison
- `bookend_analysis.png` - First-Last vs Random similarity
- `sample_surah_arcs.png` - Individual surah profiles

## Files

```
output/
  data/
    arc_profile.json     # Aggregated metrics per bin
    surah_profiles.json  # Per-surah detailed profiles
  results.json           # All results
  figures/
    *.png
```

## Conclusions

1. **No ring composition** - Bookend hypothesis not supported (ratio=0.95x)
2. **Meccan more varied** - Higher novelty at all positions
3. **Opening effect** - Lower novelty at position 0 (basmala/formulaic opening)
4. **Flat arc** - No strong intro→body→conclusion structure in embeddings

The Meccan/Medinan difference aligns with SEM-004: different rhetorical styles produce different embedding patterns.

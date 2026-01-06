# SEM-004: PCA on Quran Embeddings

**Status:** COMPLETE
**Date:** January 2026
**Result:** Data-driven axes reveal Meccan/Medinan separation and muqattaat signatures

## Objective

Find actual axes of variation in embedding space via PCA. Unlike SEM-003's synthetic poles, these are mathematically guaranteed orthogonal.

## Method

1. Load 6,236 ayah embeddings (768-dim, from SEM-001)
2. Standardize (center + scale)
3. Run PCA (top 20 components)
4. Analyze extreme ayahs per component
5. Compare Meccan vs Medinan means

## Key Results

### Variance Explained

| PC | Individual | Cumulative |
|----|------------|------------|
| 1  | 18.57%     | 18.57%     |
| 2  | 11.39%     | 29.96%     |
| 3  | 8.54%      | 38.50%     |
| 4  | 8.40%      | 46.90%     |
| 5  | 6.23%      | 53.13%     |
| **10** | - | **70.9%** |
| **20** | - | **84.6%** |

### Meccan vs Medinan Separation

| PC | Meccan Mean | Medinan Mean | Δ |
|----|-------------|--------------|---|
| **PC1** | +2.58 | -7.34 | **-9.92** |
| PC2 | +0.03 | -0.09 | -0.12 |
| PC3 | -0.08 | +0.23 | +0.31 |

PC1 strongly separates revelation periods.

### Component Interpretation (from extreme ayahs)

| PC | Positive Extreme | Negative Extreme | Interpretation |
|----|------------------|------------------|----------------|
| PC1 | Medinan legal/social | Meccan prophetic warnings | Revelation period |
| PC3 | Ha-Mim surahs | Varied | Muqattaat signature |

## Visualizations

- `variance_explained.png` - Scree plot
- `combined_pcs.png` - Top 5 PCs as flow across Quran
- `pc1_pc2_scatter.png` - 2D projection, Meccan vs Medinan
- `pc{1,2,3}_flow.png` - Individual PC trajectories

## Files

```
output/
  data/
    pc_scores.npy           # (6236, 20) PC scores
    pc_ayah_scores.json     # Per-ayah scores + metadata
    component_analysis.json # Extreme ayah analysis
  results.json              # Variance explained
  figures/
    *.png
```

## Conclusion

PCA validates:
1. **PC1 = Revelation Period** - Meccan/Medinan cleanly separable
2. **PC3 = Muqattaat** - Ha-Mim surahs cluster at positive extreme
3. 70% variance in 10 components - embedding space is lower-dimensional than expected

Data-driven approach works where synthetic poles failed.

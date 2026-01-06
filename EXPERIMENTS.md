# Experiment Registry

## Naming Convention

```
[DOMAIN]-[NUMBER]: [Short Title]
```

**Domains:**
- `MUQ` - Muqattaat (mysterious letters) studies
- `STR` - Structure analysis
- `ORD` - Ordinal/letter-order encoding
- `ENC` - General encoding experiments
- `SEM` - Semantic/LLM-based analysis

## Active Experiments

| Code | Title | Status | Key Finding |
|------|-------|--------|-------------|
| MUQ-001 | Muqattaat Theme Analysis | **COMPLETE** | Same-code surahs are ~2x more similar (p<0.002) |
| STR-001 | Structure Localization | COMPLETE | 51% cross-verse, 49% within-verse structure |
| ORD-001 | Ordinal Encoding | COMPLETE | 5-bit ordinal shows cross-word structure |
| SEM-001 | Semantic Graph | **COMPLETE** | Uniform semantic density (no clustering) |
| SEM-002 | Semantic Flow | **COMPLETE** | Surah boundaries validated (1.9x novelty) |
| SEM-003 | Semantic Axes | **INVALID** | Pole definitions not orthogonal (archived) |
| SEM-004 | PCA Analysis | **COMPLETE** | PC1 separates Meccan/Medinan (Δ=9.9), PC3=muqattaat |
| SEM-005 | Arc Analysis | **COMPLETE** | No ring composition; Meccan more varied |

## Folder Structure

```
experiments/
  MUQ-001/                    # Each experiment has its own folder
    README.md                 # Experiment description, hypothesis, results
    src/                      # Analysis scripts
    output/                   # Results, figures
      figures/
      results.json

src/
  core/                       # Framework (shared across experiments)
  encoding_functions/         # Encoding implementations

data/
  quran/                      # Source corpus
```

## File Naming

Within experiment folders:
- `analysis.py` - Main analysis script
- `visualize.py` - Visualization generation
- `results.json` - Machine-readable results
- `figures/` - Generated visualizations

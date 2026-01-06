# STR-001: Structure Localization

**Status:** COMPLETE
**Date:** January 2026

## Question

WHERE does cross-word structure exist in the Quran?

## Experiments

### 1.1 Surah-Level Analysis
Which surahs have the most cross-word structure?

**Finding:** Surahs with refrains show highest structure:
- Ar-Rahman (0.194 effect) - "Which of your Lord's favors will you deny?"
- Ash-Shu'ara (0.153 effect) - Repeated messenger narratives

### 1.2 Meccan vs Medinan
Do revelation periods differ in structure?

**Finding:** Medinan surahs show MORE cross-word structure than Meccan.

### 1.3 Verse Boundary Test
Does structure cross verse boundaries?

**Finding:**
- 51% cross-verse structure
- 49% within-verse structure
- Structure exists BOTH within and across verses

## Files

```
src/
  analysis.py       # All three experiments
output/
  results.json      # Full results
```

## Run

```bash
cd experiments/STR-001
python src/analysis.py
```

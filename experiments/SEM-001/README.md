# SEM-001: Semantic Graph of the Quran

**Status:** COMPLETE
**Date:** January 2026
**Result:** NEGATIVE (but informative)

## Objective

Build a semantic graph where each ayah (verse) is a node, edges represent semantic similarity, then analyze the resulting structure across the entire Quran (6,236 ayahs).

## Hypothesis

1. **Muqattaat validation**: Same-code surahs should cluster semantically (validates MUQ-001 with different method)
2. **Local coherence**: Ayahs within surahs are more similar than across surahs
3. **Thematic communities**: Distinct theme clusters should emerge
4. **Central ayahs**: Some ayahs are "hubs" connecting many themes

## Method

### Phase 1: Embeddings
- Use Arabic language model to embed each ayah
- Model: `paraphrase-multilingual-mpnet-base-v2` (baseline) or `AraBERT v2`
- Output: 6236 × dim embedding matrix

### Phase 2: Graph Construction
- Compute cosine similarity between all ayah pairs
- Keep top-k neighbors per node (k=20)
- Threshold edges at similarity > 0.5

### Phase 3: Analysis
- **Community detection**: Louvain algorithm
- **Centrality**: PageRank, betweenness, degree
- **Muqattaat test**: Check if same-code surahs cluster together
- **Coherence test**: Within-surah vs across-surah similarity

## Dependencies

```bash
pip install sentence-transformers networkx python-louvain numpy
# OR for AraBERT:
pip install transformers torch networkx python-louvain numpy
```

## Run

```bash
# Step 1: Generate embeddings (takes ~10-30 min)
python src/embeddings.py

# Step 2: Analyze graph structure
python src/graph_analysis.py

# Step 3: Generate visualizations (TODO)
python src/visualize.py
```

## Files

```
src/
  embeddings.py      # Generate ayah embeddings
  graph_analysis.py  # Community, centrality, coherence
  visualize.py       # Graph visualizations (TODO)
output/
  data/
    embeddings.npy   # Embedding matrix
    metadata.json    # Ayah metadata
    neighbors.json   # Sparse similarity graph
  results.json       # Analysis results
  figures/           # Visualizations
```

## Results

| Metric | Expected | Actual | Interpretation |
|--------|----------|--------|----------------|
| Within-surah similarity | > 0.6 | **0.970** | Very high everywhere |
| Across-surah similarity | ~0.5 | **0.962** | Also very high |
| Coherence ratio | > 1.2x | **1.01x** | ❌ No surah coherence |
| Muqattaat purity (Ha-Mim) | > 50% | **18%** | ❌ No clustering |
| Muqattaat purity (Alif-Lam-Ra) | > 50% | **24%** | ❌ No clustering |
| Muqattaat purity (Alif-Lam-Mim) | > 50% | **30%** | ❌ No clustering |
| Communities found | 10-30 | **18** | ✓ Expected range |

### Key Finding

**The Quran shows uniform semantic density.** Cosine similarity ~0.97 across all ayah pairs means the multilingual embedding model finds the entire text semantically cohesive.

### Hypothesis Outcomes

| # | Hypothesis | Result |
|---|------------|--------|
| 1 | Muqattaat surahs cluster semantically | **REJECTED** - purity 18-30% (random ~20%) |
| 2 | Within-surah > across-surah similarity | **REJECTED** - ratio 1.01x (no difference) |
| 3 | Distinct theme communities emerge | **PARTIAL** - 18 communities but low separation |
| 4 | Central hub ayahs exist | **CONFIRMED** - PageRank identifies hubs |

### Top 5 Central Ayahs (by PageRank)

1. At-Taghabun 64:15 - "Your wealth and children are but a trial..."
2. Al-Mumtahanah 60:4 - "There is an excellent example in Abraham..."
3. Al-Jumu'ah 62:8 - "Say: Death which you flee will meet you..."
4. Al-A'la 87:4 - "And who brought out the pasture"
5. Al-Fath 48:26 - "When those who disbelieved had put in their hearts..."

### Interpretation

The **MUQ-001 finding** (same-code surahs share vocabulary, p<0.002) operates at the **lexical level**, not semantic level. The muqattaat function as thematic/stylistic markers that group surahs by vocabulary patterns, but all surahs share the same underlying semantic space.

This is analogous to chapters in a book: they may have different vocabulary but discuss related topics within the same semantic domain.

## Current Status

- [x] Design complete
- [x] Embedding script written
- [x] Graph analysis script written
- [x] Run embeddings (6236 × 768 matrix)
- [x] Analyze results
- [ ] Visualizations
- [x] Write findings

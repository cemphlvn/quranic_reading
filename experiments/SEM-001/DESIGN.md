# SEM-001: Semantic Graph of the Quran

## Objective

Build a semantic graph where each ayah is a node, edges represent semantic similarity, then analyze the resulting structure across the entire Quran.

## Questions to Answer

1. Do muqattaat-grouped surahs cluster semantically? (validates MUQ-001 with different method)
2. What is the narrative flow? Do semantically similar ayahs appear near each other?
3. Are there semantic "bridges" connecting distant parts of the Quran?
4. Do themes form distinct communities in the graph?
5. Which ayahs are most central (connected to many others)?

## Arabic LLM Options

| Model | Type | Strength | Size |
|-------|------|----------|------|
| **Arabic-Triplet-Matryoshka-V2** | Embedding | Best STS score (69.99) | 135M |
| **GATE-AraBERT-V1** | Embedding | Second best (68.54) | 135M |
| **AraBERT v2** | Embedding | Widely tested, stable | 135M |
| **MARBERT-Matryoshka** | Embedding | Good for dialects | 135M |
| **Jais** | Generative | Best open Arabic LLM | 13B |

**Recommendation:** Start with **sentence-transformers** wrapper around AraBERT or Matryoshka models (HuggingFace). These are practical for embedding 6,236 ayahs.

## Semantic Metrics

### 1. Embedding Similarity
- Cosine similarity between ayah embeddings
- Creates the base adjacency matrix

### 2. Topic Distribution (LDA or BERTopic)
- Topic probability vector per ayah
- Jensen-Shannon divergence for topic similarity

### 3. Named Entity Overlap
- Extract: prophets, places, concepts, divine names
- Jaccard similarity of entity sets

### 4. Lexical Cohesion
- Shared root words (Arabic trilateral roots)
- Weighted by TF-IDF

### 5. Sentiment/Tone
- Mercy vs Warning classification
- Promise vs Threat
- Narrative vs Instruction

## Graph Construction

```
For each ayah pair (i, j):
    sim = weighted_combination(
        embedding_sim(i, j),
        topic_sim(i, j),
        entity_overlap(i, j),
        lexical_cohesion(i, j)
    )
    if sim > threshold:
        add_edge(i, j, weight=sim)
```

### Thresholds to Test
- Top 10 neighbors per node (k-NN graph)
- Similarity > 0.7 (high threshold)
- Similarity > 0.5 (medium threshold)

## Analysis Plan

### 1. Community Detection
- Louvain / Leiden algorithm
- Do communities align with surahs? Topics? Revelation period?

### 2. Centrality Analysis
- PageRank: most "referenced" ayahs
- Betweenness: bridges between communities
- Degree: most connected

### 3. Muqattaat Validation
- Compare to MUQ-001: do same-code surahs form tighter clusters?

### 4. Sequential Flow
- Compare semantic distance vs positional distance
- Is the Quran locally coherent? Globally structured?

### 5. Theme Extraction
- Label communities with dominant vocabulary
- Create thematic map of the Quran

## Output

1. `embeddings.npy` - 6236 x dim embedding matrix
2. `graph.json` - Edge list with weights
3. `communities.json` - Community assignments
4. `centrality.json` - Node centrality scores
5. `visualizations/` - Graph plots, heatmaps
6. `paper.html` - Results presentation

## Dependencies

```
sentence-transformers
torch
networkx
scikit-learn
community (python-louvain)
matplotlib
plotly (for interactive graph)
```

## Null Models

1. **Position shuffle**: Randomize ayah positions, compare community structure
2. **Corpus comparison**: Same analysis on Arabic poetry corpus
3. **Random graph**: Erdos-Renyi with same edge count

## Risks

- Embedding model may not capture Quranic Arabic nuances
- 6236 nodes = 19M potential edges (need efficient thresholding)
- Interpretation requires domain expertise

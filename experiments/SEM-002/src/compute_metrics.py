"""
SEM-002: Semantic Flow Metrics

Compute sequential semantic metrics across all 6,236 ayahs.
Reuses embeddings from SEM-001.
"""

import os
import json
import numpy as np
from typing import List, Dict
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM001_DATA = os.path.join(PROJECT_ROOT, 'experiments/SEM-001/output/data')


def load_data():
    """Load embeddings and metadata from SEM-001."""
    embeddings = np.load(os.path.join(SEM001_DATA, 'embeddings.npy'))

    with open(os.path.join(SEM001_DATA, 'metadata.json'), 'r') as f:
        metadata = json.load(f)

    return embeddings, metadata


def compute_novelty(embeddings: np.ndarray, window: int = 10) -> np.ndarray:
    """
    Novelty: how different is each ayah from the rolling mean of previous ayahs.
    Higher = more novel/unexpected content.
    """
    n = len(embeddings)
    novelty = np.zeros(n)

    for i in range(n):
        if i < window:
            # Not enough history, compare to what we have
            if i == 0:
                novelty[i] = 0
            else:
                prev_mean = embeddings[:i].mean(axis=0)
                novelty[i] = 1 - cosine_similarity([embeddings[i]], [prev_mean])[0, 0]
        else:
            prev_mean = embeddings[i-window:i].mean(axis=0)
            novelty[i] = 1 - cosine_similarity([embeddings[i]], [prev_mean])[0, 0]

    return novelty


def compute_coherence(embeddings: np.ndarray, window: int = 5) -> np.ndarray:
    """
    Coherence: average similarity to neighboring ayahs (±window).
    Higher = more thematically consistent with surroundings.
    """
    n = len(embeddings)
    coherence = np.zeros(n)

    for i in range(n):
        start = max(0, i - window)
        end = min(n, i + window + 1)
        neighbors = list(range(start, end))
        neighbors.remove(i)  # Exclude self

        if neighbors:
            neighbor_embs = embeddings[neighbors]
            sims = cosine_similarity([embeddings[i]], neighbor_embs)[0]
            coherence[i] = np.mean(sims)

    return coherence


def compute_shift(embeddings: np.ndarray) -> np.ndarray:
    """
    Shift: cosine distance to immediately previous ayah.
    Higher = more abrupt transition.
    """
    n = len(embeddings)
    shift = np.zeros(n)

    for i in range(1, n):
        shift[i] = 1 - cosine_similarity([embeddings[i]], [embeddings[i-1]])[0, 0]

    return shift


def compute_magnitude(embeddings: np.ndarray) -> np.ndarray:
    """
    Magnitude: L2 norm of embedding.
    May correlate with semantic richness/complexity.
    """
    return np.linalg.norm(embeddings, axis=1)


def compute_topics(embeddings: np.ndarray, n_topics: int = 15) -> tuple:
    """
    Assign each ayah to a topic cluster via k-means.
    Returns (topic_labels, cluster_centers).
    """
    kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    return labels, kmeans.cluster_centers_


def compute_topic_probability(embeddings: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """
    Soft topic assignment: similarity to each cluster center.
    Returns (n_ayahs, n_topics) matrix.
    """
    sims = cosine_similarity(embeddings, centers)
    # Normalize to probabilities
    sims = np.maximum(sims, 0)  # Ensure non-negative
    probs = sims / sims.sum(axis=1, keepdims=True)
    return probs


def find_surah_boundaries(metadata: List[Dict]) -> List[int]:
    """Find ayah indices where new surahs begin."""
    boundaries = [0]
    current_surah = metadata[0]['surah_id']

    for i, m in enumerate(metadata):
        if m['surah_id'] != current_surah:
            boundaries.append(i)
            current_surah = m['surah_id']

    return boundaries


def main():
    print("=" * 60)
    print("SEM-002: SEMANTIC FLOW METRICS")
    print("=" * 60)

    # Load data
    print("\nLoading embeddings from SEM-001...")
    embeddings, metadata = load_data()
    print(f"Loaded {len(embeddings)} ayahs")

    # Compute metrics
    print("\nComputing metrics...")

    print("  - Novelty (rolling window=10)...")
    novelty = compute_novelty(embeddings, window=10)

    print("  - Coherence (neighbor window=5)...")
    coherence = compute_coherence(embeddings, window=5)

    print("  - Shift (vs previous ayah)...")
    shift = compute_shift(embeddings)

    print("  - Magnitude (embedding norm)...")
    magnitude = compute_magnitude(embeddings)

    print("  - Topic clustering (k=15)...")
    topic_labels, topic_centers = compute_topics(embeddings, n_topics=15)
    topic_probs = compute_topic_probability(embeddings, topic_centers)

    # Find surah boundaries
    surah_boundaries = find_surah_boundaries(metadata)
    print(f"\nFound {len(surah_boundaries)} surah boundaries")

    # Analyze: do metrics spike at surah boundaries?
    boundary_set = set(surah_boundaries)
    boundary_novelty = [novelty[i] for i in boundary_set if i > 0]
    non_boundary_novelty = [novelty[i] for i in range(len(novelty)) if i not in boundary_set]

    print(f"\nNovelty at surah boundaries: {np.mean(boundary_novelty):.4f}")
    print(f"Novelty elsewhere: {np.mean(non_boundary_novelty):.4f}")
    print(f"Ratio: {np.mean(boundary_novelty)/np.mean(non_boundary_novelty):.2f}x")

    # Meccan vs Medinan
    meccan_idx = [i for i, m in enumerate(metadata) if m['type'] == 'meccan']
    medinan_idx = [i for i, m in enumerate(metadata) if m['type'] == 'medinan']

    print(f"\nMeccan ayahs: {len(meccan_idx)}")
    print(f"  Mean novelty: {np.mean(novelty[meccan_idx]):.4f}")
    print(f"  Mean coherence: {np.mean(coherence[meccan_idx]):.4f}")

    print(f"\nMedinan ayahs: {len(medinan_idx)}")
    print(f"  Mean novelty: {np.mean(novelty[medinan_idx]):.4f}")
    print(f"  Mean coherence: {np.mean(coherence[medinan_idx]):.4f}")

    # Save metrics
    output_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')
    os.makedirs(output_dir, exist_ok=True)

    metrics_per_ayah = []
    for i in range(len(embeddings)):
        metrics_per_ayah.append({
            'idx': i,
            'surah_id': metadata[i]['surah_id'],
            'verse_id': metadata[i]['verse_id'],
            'surah_name': metadata[i]['surah_name'],
            'type': metadata[i]['type'],
            'novelty': float(novelty[i]),
            'coherence': float(coherence[i]),
            'shift': float(shift[i]),
            'magnitude': float(magnitude[i]),
            'topic': int(topic_labels[i]),
        })

    with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics_per_ayah, f, indent=2)
    print(f"\nSaved metrics to {output_dir}/metrics.json")

    # Save topic probabilities as numpy
    np.save(os.path.join(output_dir, 'topic_probs.npy'), topic_probs)
    np.save(os.path.join(output_dir, 'topic_centers.npy'), topic_centers)

    # Save surah boundaries
    with open(os.path.join(output_dir, 'surah_boundaries.json'), 'w') as f:
        json.dump(surah_boundaries, f)

    # Summary results
    results = {
        'n_ayahs': len(embeddings),
        'n_topics': 15,
        'metrics': {
            'novelty': {
                'mean': float(np.mean(novelty)),
                'std': float(np.std(novelty)),
                'at_boundaries': float(np.mean(boundary_novelty)),
                'elsewhere': float(np.mean(non_boundary_novelty)),
                'boundary_ratio': float(np.mean(boundary_novelty)/np.mean(non_boundary_novelty)),
            },
            'coherence': {
                'mean': float(np.mean(coherence)),
                'std': float(np.std(coherence)),
            },
            'shift': {
                'mean': float(np.mean(shift)),
                'std': float(np.std(shift)),
            },
            'magnitude': {
                'mean': float(np.mean(magnitude)),
                'std': float(np.std(magnitude)),
            },
        },
        'meccan_vs_medinan': {
            'meccan': {
                'n': len(meccan_idx),
                'novelty': float(np.mean(novelty[meccan_idx])),
                'coherence': float(np.mean(coherence[meccan_idx])),
            },
            'medinan': {
                'n': len(medinan_idx),
                'novelty': float(np.mean(novelty[medinan_idx])),
                'coherence': float(np.mean(coherence[medinan_idx])),
            },
        },
    }

    with open(os.path.join(EXPERIMENT_ROOT, 'output/results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to output/results.json")
    print("\nDone! Next: run visualize.py")


if __name__ == "__main__":
    main()

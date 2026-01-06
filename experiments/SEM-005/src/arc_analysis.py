"""
SEM-005: Within-Surah Arc Analysis

Do surahs have internal structure (intro → body → conclusion)?
Normalize each surah to [0, 1] and track embedding patterns.
"""

import os
import json
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM001_DATA = os.path.join(PROJECT_ROOT, 'experiments/SEM-001/output/data')


def load_data():
    """Load embeddings and metadata."""
    embeddings = np.load(os.path.join(SEM001_DATA, 'embeddings.npy'))
    with open(os.path.join(SEM001_DATA, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
    return embeddings, metadata


def compute_surah_arcs(embeddings, metadata, n_bins=10):
    """
    For each surah, normalize position to [0,1] and compute metrics.
    Returns aggregated metrics per position bin.
    """
    # Group ayahs by surah
    surah_data = defaultdict(list)
    for i, m in enumerate(metadata):
        surah_data[m['surah_id']].append({
            'idx': i,
            'verse_id': m['verse_id'],
            'type': m['type'],
            'surah_name': m['surah_name'],
        })

    # Metrics per normalized position
    position_metrics = {
        'novelty': [[] for _ in range(n_bins)],
        'centroid_dist': [[] for _ in range(n_bins)],
        'first_sim': [[] for _ in range(n_bins)],
        'last_sim': [[] for _ in range(n_bins)],
    }

    surah_profiles = []

    for surah_id, ayahs in surah_data.items():
        n = len(ayahs)
        if n < 5:  # Skip very short surahs
            continue

        indices = [a['idx'] for a in ayahs]
        surah_embs = embeddings[indices]

        # Surah centroid
        centroid = surah_embs.mean(axis=0)

        # First and last embeddings
        first_emb = surah_embs[0]
        last_emb = surah_embs[-1]

        surah_profile = {
            'surah_id': surah_id,
            'surah_name': ayahs[0]['surah_name'],
            'type': ayahs[0]['type'],
            'n_ayahs': n,
            'positions': [],
        }

        for j, (a, emb) in enumerate(zip(ayahs, surah_embs)):
            # Normalized position [0, 1]
            pos = j / (n - 1) if n > 1 else 0.5
            bin_idx = min(int(pos * n_bins), n_bins - 1)

            # Novelty: distance from previous ayah
            if j > 0:
                novelty = 1 - cosine_similarity([emb], [surah_embs[j-1]])[0, 0]
            else:
                novelty = 0

            # Distance from centroid
            centroid_dist = 1 - cosine_similarity([emb], [centroid])[0, 0]

            # Similarity to first ayah
            first_sim = cosine_similarity([emb], [first_emb])[0, 0]

            # Similarity to last ayah
            last_sim = cosine_similarity([emb], [last_emb])[0, 0]

            position_metrics['novelty'][bin_idx].append(novelty)
            position_metrics['centroid_dist'][bin_idx].append(centroid_dist)
            position_metrics['first_sim'][bin_idx].append(first_sim)
            position_metrics['last_sim'][bin_idx].append(last_sim)

            surah_profile['positions'].append({
                'verse_id': a['verse_id'],
                'normalized_pos': pos,
                'novelty': float(novelty),
                'centroid_dist': float(centroid_dist),
            })

        surah_profiles.append(surah_profile)

    # Aggregate per bin
    arc_profile = {}
    for metric, bins in position_metrics.items():
        arc_profile[metric] = [float(np.mean(b)) if b else 0.0 for b in bins]

    return arc_profile, surah_profiles


def compute_bookend_similarity(embeddings, metadata):
    """
    Check if first and last ayahs of surahs are more similar than random.
    (Ring composition hypothesis)
    """
    surah_data = defaultdict(list)
    for i, m in enumerate(metadata):
        surah_data[m['surah_id']].append(i)

    first_last_sims = []
    random_sims = []

    for surah_id, indices in surah_data.items():
        if len(indices) < 5:
            continue

        first_emb = embeddings[indices[0]]
        last_emb = embeddings[indices[-1]]

        # First-last similarity
        fl_sim = cosine_similarity([first_emb], [last_emb])[0, 0]
        first_last_sims.append(fl_sim)

        # Random pair within surah
        mid = len(indices) // 2
        rand_sim = cosine_similarity([embeddings[indices[1]]], [embeddings[indices[mid]]])[0, 0]
        random_sims.append(rand_sim)

    return {
        'first_last_mean': float(np.mean(first_last_sims)),
        'first_last_std': float(np.std(first_last_sims)),
        'random_mean': float(np.mean(random_sims)),
        'random_std': float(np.std(random_sims)),
        'ratio': float(np.mean(first_last_sims) / np.mean(random_sims)),
        'n_surahs': len(first_last_sims),
    }


def main():
    print("=" * 60)
    print("SEM-005: WITHIN-SURAH ARC ANALYSIS")
    print("=" * 60)

    # Load data
    print("\nLoading embeddings...")
    embeddings, metadata = load_data()
    print(f"Loaded {len(embeddings)} ayahs")

    # Compute arc profiles
    print("\nComputing arc profiles...")
    arc_profile, surah_profiles = compute_surah_arcs(embeddings, metadata, n_bins=10)

    print("\n" + "=" * 60)
    print("ARC PROFILE (averaged across all surahs)")
    print("=" * 60)
    print("\nPosition:  ", "  ".join([f"{i/10:.1f}" for i in range(10)]))
    print("-" * 60)
    for metric, values in arc_profile.items():
        vals_str = "  ".join([f"{v:.3f}" for v in values])
        print(f"{metric:15} {vals_str}")

    # Bookend analysis
    print("\n" + "=" * 60)
    print("BOOKEND ANALYSIS (Ring Composition)")
    print("=" * 60)

    bookend = compute_bookend_similarity(embeddings, metadata)
    print(f"\n  First-Last similarity: {bookend['first_last_mean']:.3f} (±{bookend['first_last_std']:.3f})")
    print(f"  Random pair similarity: {bookend['random_mean']:.3f} (±{bookend['random_std']:.3f})")
    print(f"  Ratio: {bookend['ratio']:.3f}x")
    print(f"  Surahs analyzed: {bookend['n_surahs']}")

    if bookend['ratio'] > 1.05:
        print("\n  → First and last ayahs MORE similar than random (supports ring composition)")
    elif bookend['ratio'] < 0.95:
        print("\n  → First and last ayahs LESS similar than random")
    else:
        print("\n  → No significant difference")

    # Meccan vs Medinan arcs
    print("\n" + "=" * 60)
    print("MECCAN vs MEDINAN ARC SHAPES")
    print("=" * 60)

    meccan_profiles = [p for p in surah_profiles if p['type'] == 'meccan']
    medinan_profiles = [p for p in surah_profiles if p['type'] == 'medinan']

    def avg_arc(profiles, metric='novelty'):
        n_bins = 10
        bins = [[] for _ in range(n_bins)]
        for p in profiles:
            for pos_data in p['positions']:
                bin_idx = min(int(pos_data['normalized_pos'] * n_bins), n_bins - 1)
                bins[bin_idx].append(pos_data[metric])
        return [float(np.mean(b)) if b else 0.0 for b in bins]

    meccan_novelty = avg_arc(meccan_profiles, 'novelty')
    medinan_novelty = avg_arc(medinan_profiles, 'novelty')

    print("\nNovelty by position:")
    print("Position:  ", "  ".join([f"{i/10:.1f}" for i in range(10)]))
    print(f"Meccan:    ", "  ".join([f"{v:.3f}" for v in meccan_novelty]))
    print(f"Medinan:   ", "  ".join([f"{v:.3f}" for v in medinan_novelty]))

    # Save results
    output_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'arc_profile.json'), 'w') as f:
        json.dump(arc_profile, f, indent=2)

    with open(os.path.join(output_dir, 'surah_profiles.json'), 'w') as f:
        json.dump(surah_profiles, f, indent=2, ensure_ascii=False)

    results = {
        'arc_profile': arc_profile,
        'bookend_analysis': bookend,
        'meccan_novelty_arc': meccan_novelty,
        'medinan_novelty_arc': medinan_novelty,
    }
    with open(os.path.join(EXPERIMENT_ROOT, 'output/results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {output_dir}/")
    print("\nDone! Next: run visualize.py")


if __name__ == "__main__":
    main()

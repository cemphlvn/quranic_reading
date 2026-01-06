"""
SEM-004: PCA on Quran Embeddings

Find the actual axes of variation in the embedding space.
Data-driven, guaranteed orthogonal.
"""

import os
import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM001_DATA = os.path.join(PROJECT_ROOT, 'experiments/SEM-001/output/data')


def load_data():
    """Load embeddings and metadata."""
    embeddings = np.load(os.path.join(SEM001_DATA, 'embeddings.npy'))
    with open(os.path.join(SEM001_DATA, 'metadata.json'), 'r') as f:
        metadata = json.load(f)

    # Load Quran text for interpretation
    with open(os.path.join(PROJECT_ROOT, 'data/quran/quran.json'), 'r', encoding='utf-8') as f:
        quran = json.load(f)

    texts = []
    for surah in quran:
        for verse in surah['verses']:
            texts.append(verse['text'][:100])  # First 100 chars

    return embeddings, metadata, texts


def analyze_component(pc_scores, metadata, texts, component_idx, n_extreme=10):
    """Find and display extreme ayahs for a component."""
    scores = pc_scores[:, component_idx]

    # Most negative
    neg_idx = np.argsort(scores)[:n_extreme]
    # Most positive
    pos_idx = np.argsort(scores)[-n_extreme:][::-1]

    result = {
        'component': component_idx + 1,
        'negative_extreme': [],
        'positive_extreme': [],
    }

    for idx in neg_idx:
        result['negative_extreme'].append({
            'score': float(scores[idx]),
            'surah': metadata[idx]['surah_name'],
            'verse': metadata[idx]['verse_id'],
            'type': metadata[idx]['type'],
            'text': texts[idx],
        })

    for idx in pos_idx:
        result['positive_extreme'].append({
            'score': float(scores[idx]),
            'surah': metadata[idx]['surah_name'],
            'verse': metadata[idx]['verse_id'],
            'type': metadata[idx]['type'],
            'text': texts[idx],
        })

    return result


def main():
    print("=" * 60)
    print("SEM-004: PCA ON QURAN EMBEDDINGS")
    print("=" * 60)

    # Load data
    print("\nLoading embeddings...")
    embeddings, metadata, texts = load_data()
    print(f"Shape: {embeddings.shape}")

    # Standardize (center and scale)
    print("\nStandardizing...")
    scaler = StandardScaler()
    embeddings_scaled = scaler.fit_transform(embeddings)

    # PCA
    print("\nRunning PCA...")
    n_components = 20  # Top 20 components
    pca = PCA(n_components=n_components)
    pc_scores = pca.fit_transform(embeddings_scaled)

    # Variance explained
    print("\n" + "=" * 60)
    print("VARIANCE EXPLAINED")
    print("=" * 60)
    cumulative = 0
    for i, var in enumerate(pca.explained_variance_ratio_[:10]):
        cumulative += var
        print(f"  PC{i+1}: {var*100:5.2f}% (cumulative: {cumulative*100:5.2f}%)")

    print(f"\n  Top 10 PCs explain {cumulative*100:.1f}% of variance")
    print(f"  Top 20 PCs explain {sum(pca.explained_variance_ratio_)*100:.1f}% of variance")

    # Analyze top components
    print("\n" + "=" * 60)
    print("COMPONENT INTERPRETATION (Extreme Ayahs)")
    print("=" * 60)

    components_analysis = []
    for i in range(5):  # Top 5 components
        analysis = analyze_component(pc_scores, metadata, texts, i, n_extreme=5)
        components_analysis.append(analysis)

        print(f"\n--- PC{i+1} ({pca.explained_variance_ratio_[i]*100:.2f}% variance) ---")
        print("\nNEGATIVE extreme:")
        for item in analysis['negative_extreme'][:3]:
            print(f"  [{item['score']:.2f}] {item['surah']} {item['verse']} ({item['type']})")
            print(f"         {item['text'][:60]}...")

        print("\nPOSITIVE extreme:")
        for item in analysis['positive_extreme'][:3]:
            print(f"  [{item['score']:.2f}] {item['surah']} {item['verse']} ({item['type']})")
            print(f"         {item['text'][:60]}...")

    # Meccan vs Medinan on top PCs
    print("\n" + "=" * 60)
    print("MECCAN vs MEDINAN ON TOP PCs")
    print("=" * 60)

    meccan_idx = [i for i, m in enumerate(metadata) if m['type'] == 'meccan']
    medinan_idx = [i for i, m in enumerate(metadata) if m['type'] == 'medinan']

    for i in range(5):
        meccan_mean = pc_scores[meccan_idx, i].mean()
        medinan_mean = pc_scores[medinan_idx, i].mean()
        diff = medinan_mean - meccan_mean
        print(f"  PC{i+1}: Meccan={meccan_mean:+.3f}, Medinan={medinan_mean:+.3f}, Δ={diff:+.3f}")

    # Save results
    output_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')

    # Save PC scores
    np.save(os.path.join(output_dir, 'pc_scores.npy'), pc_scores)

    # Save per-ayah data
    ayah_data = []
    for i in range(len(metadata)):
        entry = {
            'idx': i,
            'surah_id': metadata[i]['surah_id'],
            'verse_id': metadata[i]['verse_id'],
            'surah_name': metadata[i]['surah_name'],
            'type': metadata[i]['type'],
        }
        for j in range(10):
            entry[f'pc{j+1}'] = float(pc_scores[i, j])
        ayah_data.append(entry)

    with open(os.path.join(output_dir, 'pc_ayah_scores.json'), 'w') as f:
        json.dump(ayah_data, f, indent=2)

    # Save component analysis
    with open(os.path.join(output_dir, 'component_analysis.json'), 'w') as f:
        json.dump(components_analysis, f, indent=2, ensure_ascii=False)

    # Save variance explained
    results = {
        'n_components': n_components,
        'variance_explained': pca.explained_variance_ratio_.tolist(),
        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
    }
    with open(os.path.join(EXPERIMENT_ROOT, 'output/results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {output_dir}/")
    print("\nDone! Next: run visualize.py")


if __name__ == "__main__":
    main()

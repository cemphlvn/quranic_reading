"""
SEM-004: PCA Visualizations
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM002_DATA = os.path.join(PROJECT_ROOT, 'experiments/SEM-002/output/data')

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10


def load_data():
    data_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')
    pc_scores = np.load(os.path.join(data_dir, 'pc_scores.npy'))

    with open(os.path.join(data_dir, 'pc_ayah_scores.json'), 'r') as f:
        ayah_data = json.load(f)

    with open(os.path.join(SEM002_DATA, 'surah_boundaries.json'), 'r') as f:
        boundaries = json.load(f)

    with open(os.path.join(EXPERIMENT_ROOT, 'output/results.json'), 'r') as f:
        results = json.load(f)

    return pc_scores, ayah_data, boundaries, results


def smooth(data, window=50):
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode='same')


def plot_variance_explained(results, filename='variance_explained.png'):
    """Scree plot."""
    fig, ax = plt.subplots(figsize=(10, 5))

    var = results['variance_explained'][:20]
    cum = results['cumulative_variance'][:20]

    x = range(1, len(var) + 1)
    ax.bar(x, [v * 100 for v in var], alpha=0.7, color='#3498db', label='Individual')
    ax.plot(x, [c * 100 for c in cum], 'o-', color='#e74c3c', label='Cumulative')

    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Variance Explained (%)')
    ax.set_title('PCA Variance Explained')
    ax.legend()
    ax.set_xticks(x)

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_pc_flow(pc_scores, ayah_data, boundaries, pc_idx, filename):
    """Plot a single PC across the Quran."""
    fig, ax = plt.subplots(figsize=(14, 4))

    scores = pc_scores[:, pc_idx]
    types = [a['type'] for a in ayah_data]
    colors = ['#3498db' if t == 'meccan' else '#27ae60' for t in types]

    # Scatter
    ax.scatter(range(len(scores)), scores, c=colors, s=1, alpha=0.3)

    # Smoothed
    smoothed = smooth(scores, 50)
    ax.plot(smoothed, color='#2c3e50', linewidth=1.5)

    # Zero line
    ax.axhline(y=0, color='#7f8c8d', linestyle='--', linewidth=0.5)

    # Surah boundaries
    for b in boundaries[1:]:
        ax.axvline(x=b, color='#bdc3c7', alpha=0.3, linewidth=0.5)

    ax.set_xlabel('Ayah Index')
    ax.set_ylabel(f'PC{pc_idx+1} Score')
    ax.set_title(f'Principal Component {pc_idx+1} Across the Quran')
    ax.set_xlim(0, len(scores))

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_combined_pcs(pc_scores, boundaries, filename='combined_pcs.png'):
    """Plot top 5 PCs stacked."""
    fig, axes = plt.subplots(5, 1, figsize=(14, 12), sharex=True)

    for i, ax in enumerate(axes):
        scores = pc_scores[:, i]
        smoothed = smooth(scores, 50)

        ax.fill_between(range(len(smoothed)), 0, smoothed,
                        where=(smoothed >= 0), color='#3498db', alpha=0.5)
        ax.fill_between(range(len(smoothed)), 0, smoothed,
                        where=(smoothed < 0), color='#e74c3c', alpha=0.5)
        ax.plot(smoothed, color='#2c3e50', linewidth=0.8)

        ax.axhline(y=0, color='#7f8c8d', linestyle='-', linewidth=0.5)

        for b in boundaries[1:]:
            ax.axvline(x=b, color='#bdc3c7', alpha=0.2, linewidth=0.5)

        ax.set_ylabel(f'PC{i+1}', fontsize=10)
        ax.set_xlim(0, len(scores))

    axes[-1].set_xlabel('Ayah Index')
    axes[0].set_title('Top 5 Principal Components Across the Quran')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_pc_scatter(pc_scores, ayah_data, filename='pc1_pc2_scatter.png'):
    """2D scatter of PC1 vs PC2."""
    fig, ax = plt.subplots(figsize=(10, 8))

    types = [a['type'] for a in ayah_data]
    meccan = [i for i, t in enumerate(types) if t == 'meccan']
    medinan = [i for i, t in enumerate(types) if t == 'medinan']

    ax.scatter(pc_scores[meccan, 0], pc_scores[meccan, 1],
               c='#3498db', alpha=0.3, s=5, label='Meccan')
    ax.scatter(pc_scores[medinan, 0], pc_scores[medinan, 1],
               c='#27ae60', alpha=0.3, s=5, label='Medinan')

    ax.axhline(y=0, color='#7f8c8d', linestyle='--', linewidth=0.5)
    ax.axvline(x=0, color='#7f8c8d', linestyle='--', linewidth=0.5)

    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_title('Ayahs in PC1-PC2 Space')
    ax.legend()

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def main():
    print("=" * 60)
    print("SEM-004: PCA VISUALIZATIONS")
    print("=" * 60)

    print("\nLoading data...")
    pc_scores, ayah_data, boundaries, results = load_data()

    os.makedirs(os.path.join(EXPERIMENT_ROOT, 'output/figures'), exist_ok=True)

    print("\nGenerating visualizations...")
    plot_variance_explained(results)
    plot_combined_pcs(pc_scores, boundaries)
    plot_pc_scatter(pc_scores, ayah_data)

    for i in range(3):
        plot_pc_flow(pc_scores, ayah_data, boundaries, i, f'pc{i+1}_flow.png')

    print("\nDone!")


if __name__ == "__main__":
    main()

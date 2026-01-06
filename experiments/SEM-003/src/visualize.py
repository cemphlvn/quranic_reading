"""
SEM-003: Semantic Axes Visualizations

Generate flow plots for each semantic axis across the Quran.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM002_DATA = os.path.join(PROJECT_ROOT, 'experiments/SEM-002/output/data')

# Style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.facecolor'] = 'white'

# Axis display info
AXIS_INFO = {
    'threat_mercy': {'name': 'Threat ↔ Mercy', 'neg': 'Threat', 'pos': 'Mercy', 'color_neg': '#c0392b', 'color_pos': '#27ae60'},
    'narrative_normative': {'name': 'Narrative ↔ Normative', 'neg': 'Narrative', 'pos': 'Normative', 'color_neg': '#8e44ad', 'color_pos': '#2980b9'},
    'immanence_transcendence': {'name': 'Immanence ↔ Transcendence', 'neg': 'Immanence', 'pos': 'Transcendence', 'color_neg': '#d35400', 'color_pos': '#16a085'},
    'intimacy_majesty': {'name': 'Intimacy ↔ Majesty', 'neg': 'Intimacy', 'pos': 'Majesty', 'color_neg': '#e74c3c', 'color_pos': '#3498db'},
    'certainty_contention': {'name': 'Certainty ↔ Contention', 'neg': 'Certainty', 'pos': 'Contention', 'color_neg': '#1abc9c', 'color_pos': '#e67e22'},
    'hope_fear': {'name': 'Hope ↔ Fear', 'neg': 'Hope', 'pos': 'Fear', 'color_neg': '#2ecc71', 'color_pos': '#9b59b6'},
}


def load_data():
    """Load axis scores and metadata."""
    data_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')

    with open(os.path.join(data_dir, 'axis_scores.json'), 'r') as f:
        scores = json.load(f)

    # Load surah boundaries from SEM-002
    with open(os.path.join(SEM002_DATA, 'surah_boundaries.json'), 'r') as f:
        boundaries = json.load(f)

    return scores, boundaries


def smooth(data, window=50):
    """Rolling mean smoothing."""
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode='same')


def plot_single_axis(scores, boundaries, axis_id, filename):
    """Plot a single semantic axis across the Quran."""
    info = AXIS_INFO[axis_id]
    values = np.array([s[axis_id] for s in scores])
    types = [s['type'] for s in scores]

    fig, ax = plt.subplots(figsize=(14, 4))

    # Create diverging colormap
    cmap = LinearSegmentedColormap.from_list('axis', [info['color_neg'], '#ecf0f1', info['color_pos']])

    # Scatter with color by value
    colors = [cmap((v + 0.3) / 0.6) for v in values]  # Normalize to [0,1]
    ax.scatter(range(len(values)), values, c=colors, s=2, alpha=0.3)

    # Smoothed line
    smoothed = smooth(values, 50)
    ax.plot(smoothed, color='#2c3e50', linewidth=1.5, label='Smoothed')

    # Zero line
    ax.axhline(y=0, color='#7f8c8d', linestyle='--', linewidth=0.5, alpha=0.7)

    # Surah boundaries
    for b in boundaries[1:]:
        ax.axvline(x=b, color='#bdc3c7', alpha=0.3, linewidth=0.5)

    ax.set_xlabel('Ayah Index')
    ax.set_ylabel(f'← {info["neg"]} | {info["pos"]} →')
    ax.set_title(f'Semantic Axis: {info["name"]}')
    ax.set_xlim(0, len(values))

    # Legend
    legend_elements = [
        Patch(facecolor=info['color_neg'], label=info['neg']),
        Patch(facecolor=info['color_pos'], label=info['pos']),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_all_axes_combined(scores, boundaries, filename='combined_axes.png'):
    """Plot all 6 axes in a combined figure."""
    fig, axes = plt.subplots(6, 1, figsize=(14, 16), sharex=True)

    axis_ids = list(AXIS_INFO.keys())

    for ax, axis_id in zip(axes, axis_ids):
        info = AXIS_INFO[axis_id]
        values = np.array([s[axis_id] for s in scores])
        smoothed = smooth(values, 50)

        # Plot with diverging color
        ax.fill_between(range(len(smoothed)), 0, smoothed,
                        where=(smoothed >= 0), color=info['color_pos'], alpha=0.5)
        ax.fill_between(range(len(smoothed)), 0, smoothed,
                        where=(smoothed < 0), color=info['color_neg'], alpha=0.5)
        ax.plot(smoothed, color='#2c3e50', linewidth=0.8)

        ax.axhline(y=0, color='#7f8c8d', linestyle='-', linewidth=0.5)

        # Surah boundaries
        for b in boundaries[1:]:
            ax.axvline(x=b, color='#bdc3c7', alpha=0.2, linewidth=0.5)

        ax.set_ylabel(info['name'].split('↔')[0].strip()[:8], fontsize=9)
        ax.set_xlim(0, len(values))
        ax.set_ylim(-0.25, 0.25)

    axes[-1].set_xlabel('Ayah Index')
    axes[0].set_title('All Semantic Axes Across the Quran')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_correlation_matrix(filename='axis_correlations.png'):
    """Plot correlation heatmap between axes."""
    data_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')
    corr = np.load(os.path.join(data_dir, 'axis_correlations.npy'))

    axis_ids = list(AXIS_INFO.keys())
    labels = [AXIS_INFO[aid]['name'].split('↔')[0].strip() for aid in axis_ids]

    fig, ax = plt.subplots(figsize=(8, 7))

    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)

    # Add correlation values
    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax.text(j, i, f'{corr[i, j]:.2f}',
                           ha='center', va='center', fontsize=9,
                           color='white' if abs(corr[i, j]) > 0.5 else 'black')

    ax.set_title('Semantic Axis Correlations')
    plt.colorbar(im, ax=ax, label='Correlation')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_meccan_medinan_comparison(scores, filename='meccan_medinan_axes.png'):
    """Compare axis distributions between Meccan and Medinan."""
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))

    meccan = [s for s in scores if s['type'] == 'meccan']
    medinan = [s for s in scores if s['type'] == 'medinan']

    axis_ids = list(AXIS_INFO.keys())

    for ax, axis_id in zip(axes.flat, axis_ids):
        info = AXIS_INFO[axis_id]

        meccan_vals = [s[axis_id] for s in meccan]
        medinan_vals = [s[axis_id] for s in medinan]

        ax.hist(meccan_vals, bins=40, alpha=0.6, color='#3498db', label='Meccan', density=True)
        ax.hist(medinan_vals, bins=40, alpha=0.6, color='#27ae60', label='Medinan', density=True)

        ax.axvline(x=0, color='#7f8c8d', linestyle='--', linewidth=0.5)
        ax.axvline(x=np.mean(meccan_vals), color='#3498db', linestyle='-', linewidth=2)
        ax.axvline(x=np.mean(medinan_vals), color='#27ae60', linestyle='-', linewidth=2)

        ax.set_title(info['name'], fontsize=10)
        ax.legend(fontsize=8)

    plt.suptitle('Semantic Axes: Meccan vs Medinan Distribution', fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_surah_heatmap(scores, boundaries, filename='surah_axis_heatmap.png'):
    """Heatmap of average axis values per surah."""
    # Group by surah
    surah_scores = {}
    for s in scores:
        sid = s['surah_id']
        if sid not in surah_scores:
            surah_scores[sid] = {aid: [] for aid in AXIS_INFO}
            surah_scores[sid]['type'] = s['type']
        for aid in AXIS_INFO:
            surah_scores[sid][aid].append(s[aid])

    # Compute means
    surah_ids = sorted(surah_scores.keys())
    axis_ids = list(AXIS_INFO.keys())

    matrix = np.zeros((len(axis_ids), len(surah_ids)))
    for j, sid in enumerate(surah_ids):
        for i, aid in enumerate(axis_ids):
            matrix[i, j] = np.mean(surah_scores[sid][aid])

    fig, ax = plt.subplots(figsize=(16, 5))

    im = ax.imshow(matrix, aspect='auto', cmap='RdBu_r', vmin=-0.15, vmax=0.15)

    ax.set_yticks(range(len(axis_ids)))
    ax.set_yticklabels([AXIS_INFO[aid]['name'] for aid in axis_ids], fontsize=9)

    # Mark Meccan/Medinan
    for j, sid in enumerate(surah_ids):
        if surah_scores[sid]['type'] == 'medinan':
            ax.axvline(x=j, color='#27ae60', alpha=0.3, linewidth=0.5)

    ax.set_xlabel('Surah Number')
    ax.set_title('Semantic Axes by Surah (Blue = Negative pole, Red = Positive pole)')

    plt.colorbar(im, ax=ax, label='Axis Score')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def main():
    print("=" * 60)
    print("SEM-003: SEMANTIC AXES VISUALIZATIONS")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    scores, boundaries = load_data()
    print(f"Loaded {len(scores)} ayahs")

    # Create output directory
    os.makedirs(os.path.join(EXPERIMENT_ROOT, 'output/figures'), exist_ok=True)

    # Generate plots
    print("\nGenerating visualizations...")

    # Individual axes
    for axis_id in AXIS_INFO:
        plot_single_axis(scores, boundaries, axis_id, f'axis_{axis_id}.png')

    # Combined view
    plot_all_axes_combined(scores, boundaries)

    # Correlations
    plot_correlation_matrix()

    # Meccan vs Medinan
    plot_meccan_medinan_comparison(scores)

    # Surah heatmap
    plot_surah_heatmap(scores, boundaries)

    print("\nDone! Check output/figures/")


if __name__ == "__main__":
    main()

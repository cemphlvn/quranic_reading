"""
SEM-002: Semantic Flow Visualizations

Generate plots showing how semantic metrics vary across the Quran.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.facecolor'] = 'white'


def load_data():
    """Load computed metrics."""
    data_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')

    with open(os.path.join(data_dir, 'metrics.json'), 'r') as f:
        metrics = json.load(f)

    with open(os.path.join(data_dir, 'surah_boundaries.json'), 'r') as f:
        boundaries = json.load(f)

    topic_probs = np.load(os.path.join(data_dir, 'topic_probs.npy'))

    return metrics, boundaries, topic_probs


def smooth(data, window=50):
    """Apply rolling mean for cleaner visualization."""
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode='same')


def plot_metric_flow(metrics, boundaries, metric_name, title, ylabel, filename, smooth_window=50):
    """Plot a single metric across the Quran."""
    fig, ax = plt.subplots(figsize=(14, 4))

    values = np.array([m[metric_name] for m in metrics])
    types = [m['type'] for m in metrics]

    # Color by Meccan (blue) vs Medinan (green)
    colors = ['#3498db' if t == 'meccan' else '#27ae60' for t in types]

    # Plot raw values as scatter (light)
    ax.scatter(range(len(values)), values, c=colors, alpha=0.1, s=1)

    # Plot smoothed line
    smoothed = smooth(values, smooth_window)
    ax.plot(smoothed, color='#2c3e50', linewidth=1.5, label=f'Smoothed (window={smooth_window})')

    # Mark surah boundaries
    for b in boundaries[1:]:  # Skip first (always 0)
        ax.axvline(x=b, color='#e74c3c', alpha=0.3, linewidth=0.5)

    # Mark major surahs
    major_surahs = {
        0: 'Al-Fatiha',
        7: 'Al-Baqarah',  # Approximate start indices
    }

    ax.set_xlabel('Ayah Index (sequential)')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlim(0, len(values))

    # Legend
    legend_elements = [
        Patch(facecolor='#3498db', alpha=0.5, label='Meccan'),
        Patch(facecolor='#27ae60', alpha=0.5, label='Medinan'),
        plt.Line2D([0], [0], color='#e74c3c', alpha=0.5, label='Surah boundary'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_topic_heatmap(topic_probs, boundaries, metrics, filename='topic_heatmap.png'):
    """Plot topic distribution as heatmap across Quran."""
    fig, ax = plt.subplots(figsize=(14, 6))

    # Transpose so topics are rows, ayahs are columns
    # Downsample for cleaner visualization
    step = 10
    downsampled = topic_probs[::step].T

    im = ax.imshow(downsampled, aspect='auto', cmap='YlOrRd', interpolation='nearest')

    # Mark surah boundaries (downsampled)
    for b in boundaries[1:]:
        ax.axvline(x=b//step, color='white', alpha=0.5, linewidth=0.5)

    ax.set_xlabel(f'Ayah Index (×{step})')
    ax.set_ylabel('Topic')
    ax.set_title('Topic Distribution Across the Quran')

    plt.colorbar(im, ax=ax, label='Topic Probability')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_combined_dashboard(metrics, boundaries, filename='dashboard.png'):
    """Combined dashboard of all metrics."""
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)

    n = len(metrics)
    x = range(n)

    novelty = np.array([m['novelty'] for m in metrics])
    coherence = np.array([m['coherence'] for m in metrics])
    shift = np.array([m['shift'] for m in metrics])
    topics = np.array([m['topic'] for m in metrics])

    window = 50

    # Novelty
    axes[0].plot(smooth(novelty, window), color='#9b59b6', linewidth=1)
    axes[0].set_ylabel('Novelty')
    axes[0].set_title('Semantic Flow Dashboard')

    # Coherence
    axes[1].plot(smooth(coherence, window), color='#3498db', linewidth=1)
    axes[1].set_ylabel('Coherence')

    # Shift
    axes[2].plot(smooth(shift, window), color='#e74c3c', linewidth=1)
    axes[2].set_ylabel('Shift')

    # Topic (as scatter)
    types = [m['type'] for m in metrics]
    colors = ['#3498db' if t == 'meccan' else '#27ae60' for t in types]
    axes[3].scatter(x, topics, c=colors, s=1, alpha=0.5)
    axes[3].set_ylabel('Topic')
    axes[3].set_xlabel('Ayah Index')

    # Add surah boundaries to all
    for ax in axes:
        for b in boundaries[1:]:
            ax.axvline(x=b, color='#bdc3c7', alpha=0.3, linewidth=0.5)
        ax.set_xlim(0, n)

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_meccan_medinan_comparison(metrics, filename='meccan_medinan.png'):
    """Compare metric distributions between Meccan and Medinan surahs."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    meccan = [m for m in metrics if m['type'] == 'meccan']
    medinan = [m for m in metrics if m['type'] == 'medinan']

    metric_names = ['novelty', 'coherence', 'shift', 'magnitude']
    titles = ['Novelty', 'Coherence', 'Shift', 'Magnitude']

    for ax, metric, title in zip(axes.flat, metric_names, titles):
        meccan_vals = [m[metric] for m in meccan]
        medinan_vals = [m[metric] for m in medinan]

        ax.hist(meccan_vals, bins=50, alpha=0.6, color='#3498db', label=f'Meccan (n={len(meccan)})', density=True)
        ax.hist(medinan_vals, bins=50, alpha=0.6, color='#27ae60', label=f'Medinan (n={len(medinan)})', density=True)
        ax.set_title(title)
        ax.legend()

    plt.suptitle('Meccan vs Medinan Semantic Profiles', fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_surah_profiles(metrics, boundaries, filename='surah_profiles.png'):
    """Show average metrics per surah."""
    # Group by surah
    surah_metrics = {}
    for m in metrics:
        sid = m['surah_id']
        if sid not in surah_metrics:
            surah_metrics[sid] = {'novelty': [], 'coherence': [], 'shift': [], 'type': m['type'], 'name': m['surah_name']}
        surah_metrics[sid]['novelty'].append(m['novelty'])
        surah_metrics[sid]['coherence'].append(m['coherence'])
        surah_metrics[sid]['shift'].append(m['shift'])

    # Compute means
    surah_ids = sorted(surah_metrics.keys())
    novelty_means = [np.mean(surah_metrics[s]['novelty']) for s in surah_ids]
    coherence_means = [np.mean(surah_metrics[s]['coherence']) for s in surah_ids]
    types = [surah_metrics[s]['type'] for s in surah_ids]
    colors = ['#3498db' if t == 'meccan' else '#27ae60' for t in types]

    fig, axes = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

    axes[0].bar(surah_ids, novelty_means, color=colors, alpha=0.7)
    axes[0].set_ylabel('Mean Novelty')
    axes[0].set_title('Semantic Profile by Surah')

    axes[1].bar(surah_ids, coherence_means, color=colors, alpha=0.7)
    axes[1].set_ylabel('Mean Coherence')
    axes[1].set_xlabel('Surah Number')

    # Legend
    legend_elements = [
        Patch(facecolor='#3498db', alpha=0.7, label='Meccan'),
        Patch(facecolor='#27ae60', alpha=0.7, label='Medinan'),
    ]
    axes[0].legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def main():
    print("=" * 60)
    print("SEM-002: SEMANTIC FLOW VISUALIZATIONS")
    print("=" * 60)

    # Load data
    print("\nLoading metrics...")
    metrics, boundaries, topic_probs = load_data()
    print(f"Loaded {len(metrics)} ayahs, {len(boundaries)} surah boundaries")

    # Create output directory
    os.makedirs(os.path.join(EXPERIMENT_ROOT, 'output/figures'), exist_ok=True)

    # Generate plots
    print("\nGenerating visualizations...")

    plot_metric_flow(metrics, boundaries, 'novelty',
                     'Semantic Novelty Across the Quran',
                     'Novelty (distance from recent context)',
                     'flow_novelty.png')

    plot_metric_flow(metrics, boundaries, 'coherence',
                     'Local Coherence Across the Quran',
                     'Coherence (similarity to neighbors)',
                     'flow_coherence.png')

    plot_metric_flow(metrics, boundaries, 'shift',
                     'Semantic Shift Across the Quran',
                     'Shift (distance to previous ayah)',
                     'flow_shift.png')

    plot_topic_heatmap(topic_probs, boundaries, metrics)

    plot_combined_dashboard(metrics, boundaries)

    plot_meccan_medinan_comparison(metrics)

    plot_surah_profiles(metrics, boundaries)

    print("\nDone! Check output/figures/")


if __name__ == "__main__":
    main()

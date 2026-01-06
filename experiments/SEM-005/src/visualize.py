"""
SEM-005: Arc Analysis Visualizations
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt

EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10


def load_data():
    with open(os.path.join(EXPERIMENT_ROOT, 'output/results.json'), 'r') as f:
        results = json.load(f)
    with open(os.path.join(EXPERIMENT_ROOT, 'output/data/surah_profiles.json'), 'r') as f:
        surah_profiles = json.load(f)
    return results, surah_profiles


def plot_arc_profile(results, filename='arc_profile.png'):
    """Plot the average arc profile."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    arc = results['arc_profile']
    x = np.linspace(0, 1, 10)

    metrics = [
        ('novelty', 'Novelty (distance from previous)', '#9b59b6'),
        ('centroid_dist', 'Distance from Surah Centroid', '#e74c3c'),
        ('first_sim', 'Similarity to First Ayah', '#3498db'),
        ('last_sim', 'Similarity to Last Ayah', '#27ae60'),
    ]

    for ax, (key, title, color) in zip(axes.flat, metrics):
        values = arc[key]
        ax.plot(x, values, 'o-', color=color, linewidth=2, markersize=8)
        ax.fill_between(x, values, alpha=0.2, color=color)
        ax.set_xlabel('Normalized Position in Surah')
        ax.set_ylabel(title)
        ax.set_title(title)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xticklabels(['Start', '25%', 'Middle', '75%', 'End'])

    plt.suptitle('Within-Surah Arc Profile (All Surahs Averaged)', fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_meccan_medinan_arcs(results, filename='meccan_medinan_arcs.png'):
    """Compare Meccan vs Medinan arc shapes."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.linspace(0, 1, 10)
    meccan = results['meccan_novelty_arc']
    medinan = results['medinan_novelty_arc']

    ax.plot(x, meccan, 'o-', color='#3498db', linewidth=2, markersize=8, label='Meccan')
    ax.plot(x, medinan, 's-', color='#27ae60', linewidth=2, markersize=8, label='Medinan')

    ax.fill_between(x, meccan, alpha=0.2, color='#3498db')
    ax.fill_between(x, medinan, alpha=0.2, color='#27ae60')

    ax.set_xlabel('Normalized Position in Surah')
    ax.set_ylabel('Novelty (distance from previous ayah)')
    ax.set_title('Within-Surah Novelty Arc: Meccan vs Medinan')
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(['Start', '25%', 'Middle', '75%', 'End'])
    ax.legend()

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_bookend_comparison(results, filename='bookend_analysis.png'):
    """Visualize bookend (ring composition) analysis."""
    fig, ax = plt.subplots(figsize=(8, 6))

    bookend = results['bookend_analysis']

    categories = ['First-Last\nSimilarity', 'Random Pair\nSimilarity']
    means = [bookend['first_last_mean'], bookend['random_mean']]
    stds = [bookend['first_last_std'], bookend['random_std']]

    bars = ax.bar(categories, means, yerr=stds, capsize=5,
                  color=['#3498db', '#95a5a6'], alpha=0.8)

    ax.set_ylabel('Cosine Similarity')
    ax.set_title(f'Bookend Analysis: First vs Last Ayah Similarity\n(n={bookend["n_surahs"]} surahs, ratio={bookend["ratio"]:.2f}x)')

    # Add value labels
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def plot_individual_surahs(surah_profiles, filename='sample_surah_arcs.png'):
    """Plot arc profiles for a few individual surahs."""
    # Select interesting surahs
    target_names = ['Al-Baqarah', 'Yusuf', 'Ar-Rahman', 'Al-Mulk']
    selected = [p for p in surah_profiles if p['surah_name'] in target_names]

    if len(selected) < 2:
        selected = surah_profiles[:4]  # Fallback

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    for ax, profile in zip(axes.flat, selected[:4]):
        positions = [p['normalized_pos'] for p in profile['positions']]
        novelty = [p['novelty'] for p in profile['positions']]

        ax.plot(positions, novelty, '-', alpha=0.5, color='#3498db')
        ax.scatter(positions, novelty, s=10, c='#3498db', alpha=0.7)

        ax.set_xlabel('Position in Surah')
        ax.set_ylabel('Novelty')
        ax.set_title(f"{profile['surah_name']} ({profile['n_ayahs']} ayahs, {profile['type']})")
        ax.set_xlim(0, 1)

    plt.suptitle('Individual Surah Arc Profiles', fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(EXPERIMENT_ROOT, f'output/figures/{filename}'), dpi=150)
    plt.close()
    print(f"  Saved {filename}")


def main():
    print("=" * 60)
    print("SEM-005: ARC ANALYSIS VISUALIZATIONS")
    print("=" * 60)

    print("\nLoading data...")
    results, surah_profiles = load_data()

    os.makedirs(os.path.join(EXPERIMENT_ROOT, 'output/figures'), exist_ok=True)

    print("\nGenerating visualizations...")
    plot_arc_profile(results)
    plot_meccan_medinan_arcs(results)
    plot_bookend_comparison(results)
    plot_individual_surahs(surah_profiles)

    print("\nDone!")


if __name__ == "__main__":
    main()

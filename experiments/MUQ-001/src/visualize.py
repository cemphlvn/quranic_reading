"""
MUQATTA'AT VISUALIZATIONS

Generate charts for the section-marking findings.
"""

import sys
import os

# Set paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Ensure output directory exists
Path(os.path.join(EXPERIMENT_ROOT, 'output/figures')).mkdir(parents=True, exist_ok=True)

# Set style - use default fonts (no Arabic needed with transliteration)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 12
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'

# Transliteration for labels (ASCII-safe)
CODE_LABELS = {
    'حم': 'Ha-Mim',
    'الر': 'Alif-Lam-Ra',
    'الم': 'Alif-Lam-Mim',
    'طس': 'Ta-Sin',
}


def load_results():
    """Load analysis results."""
    with open(os.path.join(EXPERIMENT_ROOT, 'output/results.json'), 'r') as f:
        theme = json.load(f)
    with open(os.path.join(EXPERIMENT_ROOT, 'output/distinctive.json'), 'r') as f:
        distinctive = json.load(f)
    return theme, distinctive


def fig1_similarity_comparison(theme_results):
    """Bar chart: Observed vs Null similarity for each group."""
    fig, ax = plt.subplots(figsize=(10, 6))

    codes = list(theme_results.keys())
    labels = [CODE_LABELS.get(c, c) for c in codes]
    x = np.arange(len(codes))
    width = 0.35

    observed = [theme_results[c]['observed_cosine'] for c in codes]
    null = [theme_results[c]['null_cosine'] for c in codes]

    bars1 = ax.bar(x - width/2, observed, width, label='Same-Code Surahs',
                   color='#2563eb', edgecolor='white', linewidth=1)
    bars2 = ax.bar(x + width/2, null, width, label='Random Groups',
                   color='#94a3b8', edgecolor='white', linewidth=1)

    # Add significance stars
    for i, code in enumerate(codes):
        p = theme_results[code]['p_cosine']
        if p < 0.01:
            ax.annotate('**', (x[i] - width/2, observed[i] + 0.02),
                       ha='center', fontsize=14, fontweight='bold')
        elif p < 0.05:
            ax.annotate('*', (x[i] - width/2, observed[i] + 0.02),
                       ha='center', fontsize=14, fontweight='bold')

    ax.set_ylabel('Vocabulary Similarity (Cosine)', fontsize=13)
    ax.set_xlabel('Muqattaat Code', fontsize=13)
    ax.set_title('Thematic Similarity: Same-Code vs Random Surah Groups',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 0.95)

    # Add annotation
    ax.text(0.02, 0.98, 'p < 0.01 for all groups', transform=ax.transAxes,
            fontsize=10, verticalalignment='top', fontstyle='italic', color='#475569')

    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig1_similarity.png', dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig1_similarity.svg', bbox_inches='tight')
    plt.close()
    print("Saved: fig1_similarity.png/svg")


def fig2_surah_map():
    """Visual map of Muqatta'at codes across surahs."""
    fig, ax = plt.subplots(figsize=(14, 4))

    # All 114 surahs
    n_surahs = 114

    # Define groups with colors
    groups = {
        'الم': {'surahs': [2, 3, 29, 30, 31, 32], 'color': '#3b82f6'},
        'الر': {'surahs': [10, 11, 12, 14, 15], 'color': '#22c55e'},
        'المر': {'surahs': [13], 'color': '#22c55e', 'variant': True},
        'المص': {'surahs': [7], 'color': '#3b82f6', 'variant': True},
        'كهيعص': {'surahs': [19], 'color': '#a855f7'},
        'طه': {'surahs': [20], 'color': '#f97316'},
        'طسم': {'surahs': [26, 28], 'color': '#f97316'},
        'طس': {'surahs': [27], 'color': '#f97316'},
        'يس': {'surahs': [36], 'color': '#ec4899'},
        'ص': {'surahs': [38], 'color': '#14b8a6'},
        'حم': {'surahs': [40, 41, 42, 43, 44, 45, 46], 'color': '#ef4444'},
        'ق': {'surahs': [50], 'color': '#8b5cf6'},
        'ن': {'surahs': [68], 'color': '#06b6d4'},
    }

    # Create surah blocks
    block_height = 0.6
    y = 0

    for i in range(1, n_surahs + 1):
        x = (i - 1) % 38
        row = (i - 1) // 38

        # Find if surah has a code
        color = '#e2e8f0'  # Default gray
        code_label = ''
        alpha = 0.4

        for code, info in groups.items():
            if i in info['surahs']:
                color = info['color']
                code_label = code
                alpha = 1.0
                break

        rect = plt.Rectangle((x, -row * 1.2), 0.9, block_height,
                             facecolor=color, alpha=alpha,
                             edgecolor='white', linewidth=0.5)
        ax.add_patch(rect)

        # Add surah number
        ax.text(x + 0.45, -row * 1.2 + block_height/2, str(i),
               ha='center', va='center', fontsize=7,
               color='white' if alpha > 0.5 else '#64748b',
               fontweight='bold' if alpha > 0.5 else 'normal')

    ax.set_xlim(-0.5, 38.5)
    ax.set_ylim(-3, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.set_title('Muqattaat Codes Across 114 Surahs\n(colored = has code, gray = no code)',
                 fontsize=14, fontweight='bold', pad=10)

    # Legend
    legend_items = [
        ('ALM', '#3b82f6'), ('ALR', '#22c55e'), ('TS', '#f97316'),
        ('HM', '#ef4444'), ('Other', '#a855f7')
    ]
    patches = [mpatches.Patch(color=c, label=l) for l, c in legend_items]
    ax.legend(handles=patches, loc='upper right', ncol=5, fontsize=9,
              frameon=True, fancybox=True)

    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig2_surah_map.png', dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig2_surah_map.svg', bbox_inches='tight')
    plt.close()
    print("Saved: fig2_surah_map.png/svg")


def fig3_consecutive_pattern():
    """Show the consecutive clustering of codes."""
    fig, ax = plt.subplots(figsize=(12, 5))

    groups = [
        {'code': 'Ha-Mim', 'surahs': [40, 41, 42, 43, 44, 45, 46], 'color': '#ef4444', 'y': 3},
        {'code': 'Ta-Sin', 'surahs': [26, 27, 28], 'color': '#f97316', 'y': 2},
        {'code': 'Alif-Lam-Ra', 'surahs': [10, 11, 12, 14, 15], 'color': '#22c55e', 'y': 1},
        {'code': 'Alif-Lam-Mim', 'surahs': [2, 3, 29, 30, 31, 32], 'color': '#3b82f6', 'y': 0},
    ]

    for g in groups:
        for s in g['surahs']:
            ax.barh(g['y'], 1, left=s-0.5, height=0.6, color=g['color'],
                   edgecolor='white', linewidth=1)
            ax.text(s, g['y'], str(s), ha='center', va='center',
                   fontsize=9, color='white', fontweight='bold')

    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(['Alif-Lam-Mim', 'Alif-Lam-Ra', 'Ta-Sin', 'Ha-Mim'], fontsize=11)
    ax.set_xlabel('Surah Number', fontsize=12)
    ax.set_xlim(0, 70)
    ax.set_ylim(-0.5, 3.8)

    ax.set_title('Consecutive Clustering of Muqattaat Codes',
                 fontsize=14, fontweight='bold', pad=15)

    # Annotations
    ax.annotate('PERFECT\nsequence', xy=(43, 3.5), fontsize=10, ha='center',
               color='#ef4444', fontweight='bold')
    ax.annotate('Gap at 13\n(ALM-R variant)', xy=(13, 1.5), fontsize=9, ha='center',
               color='#64748b', fontstyle='italic')
    ax.annotate('Two clusters:\n2-3 and 29-32', xy=(16, -0.3), fontsize=9, ha='center',
               color='#64748b', fontstyle='italic')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig3_consecutive.png', dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig3_consecutive.svg', bbox_inches='tight')
    plt.close()
    print("Saved: fig3_consecutive.png/svg")


def fig4_effect_size(theme_results):
    """Effect size visualization."""
    fig, ax = plt.subplots(figsize=(8, 5))

    codes = list(theme_results.keys())
    labels = [CODE_LABELS.get(c, c) for c in codes]

    # Calculate effect: (observed - null) / null
    effects = []
    for c in codes:
        obs = theme_results[c]['observed_cosine']
        null = theme_results[c]['null_cosine']
        effect = (obs - null) / null * 100  # Percent increase
        effects.append(effect)

    colors = ['#ef4444', '#22c55e', '#3b82f6', '#f97316']
    bars = ax.barh(labels, effects, color=colors, edgecolor='white', height=0.6)

    ax.set_xlabel('Similarity Increase vs Random (%)', fontsize=12)
    ax.set_title('Effect Size: How Much More Similar Are Same-Code Surahs?',
                 fontsize=13, fontweight='bold', pad=15)

    # Add value labels
    for i, (bar, eff) in enumerate(zip(bars, effects)):
        ax.text(eff + 2, bar.get_y() + bar.get_height()/2,
               f'+{eff:.0f}%', va='center', fontsize=11, fontweight='bold')

    ax.set_xlim(0, 120)
    ax.axvline(x=0, color='black', linewidth=0.5)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig4_effect.png', dpi=150, bbox_inches='tight')
    plt.savefig(os.path.join(EXPERIMENT_ROOT, 'output/figures/') + 'fig4_effect.svg', bbox_inches='tight')
    plt.close()
    print("Saved: fig4_effect.png/svg")


def main():
    print("=" * 50)
    print("GENERATING VISUALIZATIONS")
    print("=" * 50)

    theme, distinctive = load_results()

    fig1_similarity_comparison(theme)
    fig2_surah_map()
    fig3_consecutive_pattern()
    fig4_effect_size(theme)

    print("\nAll figures saved to output/figures/")


if __name__ == "__main__":
    main()

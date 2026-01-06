"""
SEM-001: Semantic Graph Analysis

Analyze the semantic graph structure:
- Community detection
- Centrality analysis
- Muqattaat validation
- Thematic structure
"""

import sys
import os
import json
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_data():
    """Load embeddings and metadata."""
    data_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')

    embeddings = np.load(os.path.join(data_dir, 'embeddings.npy'))

    with open(os.path.join(data_dir, 'metadata.json'), 'r') as f:
        metadata = json.load(f)

    with open(os.path.join(data_dir, 'neighbors.json'), 'r') as f:
        neighbors = json.load(f)
        # Convert string keys to int
        neighbors = {int(k): v for k, v in neighbors.items()}

    return embeddings, metadata, neighbors


def build_networkx_graph(neighbors: Dict, threshold: float = 0.5):
    """Build NetworkX graph from neighbor dict."""
    import networkx as nx

    G = nx.Graph()

    # Add all nodes
    n_nodes = len(neighbors)
    G.add_nodes_from(range(n_nodes))

    # Add edges above threshold
    for node_id, neighbor_list in neighbors.items():
        for neighbor_id, similarity in neighbor_list:
            if similarity >= threshold and node_id < neighbor_id:  # Avoid duplicates
                G.add_edge(node_id, neighbor_id, weight=similarity)

    return G


def detect_communities(G) -> Dict[int, int]:
    """Detect communities using Louvain algorithm."""
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(G, weight='weight')
        return partition
    except ImportError:
        print("python-louvain not installed. Install with: pip install python-louvain")
        return {}


def compute_centrality(G) -> Dict:
    """Compute various centrality measures."""
    import networkx as nx

    print("Computing PageRank...")
    pagerank = nx.pagerank(G, weight='weight')

    print("Computing degree centrality...")
    degree = dict(G.degree(weight='weight'))

    print("Computing betweenness (sampling)...")
    # Sample for speed on large graphs
    betweenness = nx.betweenness_centrality(G, k=min(500, len(G)))

    return {
        'pagerank': pagerank,
        'degree': degree,
        'betweenness': betweenness
    }


def analyze_muqattaat(metadata: List[Dict], communities: Dict[int, int]) -> Dict:
    """Check if muqattaat-grouped surahs end up in same communities."""

    MUQATTAAT_GROUPS = {
        'Ha-Mim': [40, 41, 42, 43, 44, 45, 46],
        'Alif-Lam-Ra': [10, 11, 12, 14, 15],
        'Alif-Lam-Mim': [2, 3, 29, 30, 31, 32],
        'Ta-Sin': [26, 27, 28],
    }

    results = {}

    for code, surah_ids in MUQATTAAT_GROUPS.items():
        # Find all ayahs in these surahs
        group_communities = []
        for idx, m in enumerate(metadata):
            if m['surah_id'] in surah_ids and idx in communities:
                group_communities.append(communities[idx])

        if group_communities:
            # Count community membership
            community_counts = defaultdict(int)
            for c in group_communities:
                community_counts[c] += 1

            # Find dominant community
            dominant = max(community_counts, key=community_counts.get)
            purity = community_counts[dominant] / len(group_communities)

            results[code] = {
                'n_ayahs': len(group_communities),
                'n_communities': len(set(group_communities)),
                'dominant_community': dominant,
                'purity': purity,  # Fraction in dominant community
            }

    return results


def analyze_surah_coherence(metadata: List[Dict], neighbors: Dict) -> Dict:
    """Analyze if ayahs within surahs are more similar than across surahs."""

    # Group ayahs by surah
    surah_ayahs = defaultdict(list)
    for idx, m in enumerate(metadata):
        surah_ayahs[m['surah_id']].append(idx)

    within_surah_sims = []
    across_surah_sims = []

    for idx, neighbor_list in neighbors.items():
        idx_surah = metadata[idx]['surah_id']

        for neighbor_id, sim in neighbor_list[:10]:  # Top 10 neighbors
            neighbor_surah = metadata[neighbor_id]['surah_id']

            if neighbor_surah == idx_surah:
                within_surah_sims.append(sim)
            else:
                across_surah_sims.append(sim)

    return {
        'within_surah_mean': np.mean(within_surah_sims) if within_surah_sims else 0,
        'across_surah_mean': np.mean(across_surah_sims) if across_surah_sims else 0,
        'n_within': len(within_surah_sims),
        'n_across': len(across_surah_sims),
    }


def find_central_ayahs(metadata: List[Dict], centrality: Dict, top_k: int = 20) -> List[Dict]:
    """Find most central ayahs by PageRank."""

    pagerank = centrality['pagerank']
    sorted_nodes = sorted(pagerank.keys(), key=lambda x: pagerank[x], reverse=True)

    # Load Quran text for display
    with open(os.path.join(PROJECT_ROOT, 'data/quran/quran.json'), 'r', encoding='utf-8') as f:
        quran = json.load(f)

    # Build lookup
    text_lookup = {}
    for surah in quran:
        for verse in surah['verses']:
            key = (surah['id'], verse['id'])
            text_lookup[key] = verse['text'][:100] + '...' if len(verse['text']) > 100 else verse['text']

    results = []
    for node in sorted_nodes[:top_k]:
        m = metadata[node]
        key = (m['surah_id'], m['verse_id'])
        results.append({
            'rank': len(results) + 1,
            'surah': m['surah_name'],
            'verse': m['verse_id'],
            'pagerank': pagerank[node],
            'text_preview': text_lookup.get(key, '')
        })

    return results


def main():
    print("=" * 60)
    print("SEM-001: SEMANTIC GRAPH ANALYSIS")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    try:
        embeddings, metadata, neighbors = load_data()
    except FileNotFoundError:
        print("Data not found. Run embeddings.py first.")
        return

    print(f"Loaded {len(metadata)} ayahs")

    # Build graph
    print("\nBuilding graph (threshold=0.5)...")
    try:
        import networkx as nx
    except ImportError:
        print("networkx not installed. Install with: pip install networkx")
        return

    G = build_networkx_graph(neighbors, threshold=0.5)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Community detection
    print("\nDetecting communities...")
    communities = detect_communities(G)
    if communities:
        n_communities = len(set(communities.values()))
        print(f"Found {n_communities} communities")
    else:
        print("Skipping community analysis (library not installed)")

    # Centrality
    print("\nComputing centrality...")
    centrality = compute_centrality(G)

    # Muqattaat analysis
    if communities:
        print("\nAnalyzing muqattaat groupings...")
        muq_results = analyze_muqattaat(metadata, communities)
        print("\nMuqattaat Community Purity:")
        for code, r in muq_results.items():
            print(f"  {code}: {r['purity']:.1%} in dominant community ({r['n_communities']} communities total)")

    # Surah coherence
    print("\nAnalyzing surah coherence...")
    coherence = analyze_surah_coherence(metadata, neighbors)
    print(f"Within-surah similarity: {coherence['within_surah_mean']:.3f}")
    print(f"Across-surah similarity: {coherence['across_surah_mean']:.3f}")
    ratio = coherence['within_surah_mean'] / coherence['across_surah_mean'] if coherence['across_surah_mean'] > 0 else 0
    print(f"Ratio: {ratio:.2f}x (higher = more coherent surahs)")

    # Central ayahs
    print("\nMost central ayahs (by PageRank):")
    central = find_central_ayahs(metadata, centrality, top_k=10)
    for a in central:
        print(f"  {a['rank']}. {a['surah']} {a['verse']}: {a['text_preview']}")

    # Save results
    output_dir = os.path.join(EXPERIMENT_ROOT, 'output')

    results = {
        'graph_stats': {
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'n_communities': len(set(communities.values())) if communities else 0,
        },
        'surah_coherence': coherence,
        'muqattaat': muq_results if communities else {},
        'top_central_ayahs': central,
    }

    with open(os.path.join(output_dir, 'results.json'), 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()

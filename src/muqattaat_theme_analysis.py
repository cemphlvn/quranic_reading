"""
MUQATTA'AT THEME ANALYSIS

Does the section-marking system correlate with THEMES?

Hypothesis: If Muqatta'at are navigation markers, same-code surahs
should share thematic content more than random surahs.

Method:
1. Extract vocabulary from each surah
2. Compare within-group similarity vs between-group similarity
3. Statistical test: Is within-group similarity significantly higher?
"""

import sys
sys.path.insert(0, 'src')
import json
import random
from collections import Counter
from typing import List, Dict, Set
import re

# Muqatta'at groups (from previous analysis)
MUQATTAAT_GROUPS = {
    'حم': [40, 41, 42, 43, 44, 45, 46],  # Ha-Mim: CONSECUTIVE
    'الر': [10, 11, 12, 14, 15],          # Alif-Lam-Ra: nearly consecutive
    'الم': [2, 3, 29, 30, 31, 32],        # Alif-Lam-Mim: two clusters
    'طس': [26, 27, 28],                   # Ta-Sin variants (26=طسم, 27=طس, 28=طسم)
}

# Isolated markers (single surahs)
ISOLATED = {
    'المص': [7],
    'المر': [13],
    'كهيعص': [19],
    'طه': [20],
    'يس': [36],
    'ص': [38],
    'ق': [50],
    'ن': [68],
}

DIACRITICS = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')

def strip_diacritics(text: str) -> str:
    return DIACRITICS.sub('', text)


def extract_words(text: str) -> List[str]:
    """Extract Arabic words (normalized)."""
    text = strip_diacritics(text)
    words = re.findall(r'[\u0621-\u064A]+', text)
    return words


def get_vocabulary(verses: List[Dict]) -> Counter:
    """Get word frequency counter for a surah."""
    all_words = []
    for v in verses:
        all_words.extend(extract_words(v['text']))
    return Counter(all_words)


def jaccard_similarity(vocab1: Counter, vocab2: Counter) -> float:
    """Jaccard similarity between two vocabularies."""
    set1 = set(vocab1.keys())
    set2 = set(vocab2.keys())
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union


def cosine_similarity(vocab1: Counter, vocab2: Counter) -> float:
    """Cosine similarity between two vocabulary frequency vectors."""
    all_words = set(vocab1.keys()) | set(vocab2.keys())
    if not all_words:
        return 0.0

    dot = sum(vocab1.get(w, 0) * vocab2.get(w, 0) for w in all_words)
    norm1 = sum(v**2 for v in vocab1.values()) ** 0.5
    norm2 = sum(v**2 for v in vocab2.values()) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def analyze_group_similarity(data: List[Dict], surah_ids: List[int],
                            all_vocabs: Dict[int, Counter]) -> Dict:
    """Compute pairwise similarities within a group."""
    if len(surah_ids) < 2:
        return {"n_pairs": 0, "jaccard_pairs": [], "cosine_pairs": []}

    jaccard_pairs = []
    cosine_pairs = []

    for i, s1 in enumerate(surah_ids):
        for s2 in surah_ids[i+1:]:
            if s1 in all_vocabs and s2 in all_vocabs:
                j = jaccard_similarity(all_vocabs[s1], all_vocabs[s2])
                c = cosine_similarity(all_vocabs[s1], all_vocabs[s2])
                jaccard_pairs.append(j)
                cosine_pairs.append(c)

    return {
        "n_pairs": len(jaccard_pairs),
        "jaccard_pairs": jaccard_pairs,
        "cosine_pairs": cosine_pairs,
        "jaccard_mean": sum(jaccard_pairs)/len(jaccard_pairs) if jaccard_pairs else 0,
        "cosine_mean": sum(cosine_pairs)/len(cosine_pairs) if cosine_pairs else 0,
    }


def random_group_similarity(all_vocabs: Dict[int, Counter],
                           group_size: int, n_samples: int = 100,
                           seed: int = 42) -> Dict:
    """Compute similarity for random groups of same size."""
    rng = random.Random(seed)
    all_ids = list(all_vocabs.keys())

    jaccard_samples = []
    cosine_samples = []

    for _ in range(n_samples):
        sample = rng.sample(all_ids, min(group_size, len(all_ids)))
        result = analyze_group_similarity(None, sample, all_vocabs)
        if result['jaccard_pairs']:
            jaccard_samples.append(result['jaccard_mean'])
            cosine_samples.append(result['cosine_mean'])

    return {
        "jaccard_null": jaccard_samples,
        "cosine_null": cosine_samples,
        "jaccard_mean": sum(jaccard_samples)/len(jaccard_samples) if jaccard_samples else 0,
        "cosine_mean": sum(cosine_samples)/len(cosine_samples) if cosine_samples else 0,
    }


def main():
    print("=" * 60)
    print("MUQATTA'AT THEME ANALYSIS")
    print("=" * 60)
    print("\nQuestion: Do same-code surahs share themes?")
    print("Method: Vocabulary similarity within vs between groups")

    # Load data
    print("\nLoading Quran...")
    with open('data/quran/quran.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build vocabulary for each surah
    print("Building vocabulary profiles...")
    all_vocabs = {}
    surah_names = {}
    for surah in data:
        sid = surah['id']
        all_vocabs[sid] = get_vocabulary(surah['verses'])
        surah_names[sid] = surah['transliteration']

    print(f"Processed {len(all_vocabs)} surahs")

    # Analyze each Muqatta'at group
    print("\n" + "=" * 60)
    print("WITHIN-GROUP SIMILARITY")
    print("=" * 60)

    results = {}

    for code, surah_ids in MUQATTAAT_GROUPS.items():
        print(f"\n{code} group: surahs {surah_ids}")
        print(f"  Names: {[surah_names.get(s, '?') for s in surah_ids]}")

        group_result = analyze_group_similarity(data, surah_ids, all_vocabs)

        # Compare to random groups of same size
        null_result = random_group_similarity(all_vocabs, len(surah_ids), n_samples=500)

        # P-value: how often does random beat observed?
        observed_j = group_result['jaccard_mean']
        observed_c = group_result['cosine_mean']

        p_jaccard = sum(1 for x in null_result['jaccard_null'] if x >= observed_j) / len(null_result['jaccard_null'])
        p_cosine = sum(1 for x in null_result['cosine_null'] if x >= observed_c) / len(null_result['cosine_null'])

        sig_j = "***" if p_jaccard < 0.05 else ""
        sig_c = "***" if p_cosine < 0.05 else ""

        print(f"  Jaccard: observed={observed_j:.3f}, null={null_result['jaccard_mean']:.3f}, p={p_jaccard:.3f} {sig_j}")
        print(f"  Cosine:  observed={observed_c:.3f}, null={null_result['cosine_mean']:.3f}, p={p_cosine:.3f} {sig_c}")

        results[code] = {
            'surah_ids': surah_ids,
            'observed_jaccard': observed_j,
            'observed_cosine': observed_c,
            'null_jaccard': null_result['jaccard_mean'],
            'null_cosine': null_result['cosine_mean'],
            'p_jaccard': p_jaccard,
            'p_cosine': p_cosine,
        }

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    significant_groups = []
    for code, r in results.items():
        if r['p_jaccard'] < 0.05 or r['p_cosine'] < 0.05:
            significant_groups.append(code)

    print(f"\nGroups with significant thematic clustering: {significant_groups}")

    if significant_groups:
        print("""
FINDING: Some Muqatta'at groups DO share themes!

This supports the SECTION-MARKING hypothesis:
- Same codes mark thematically related surahs
- The consecutive placement is NOT coincidental
- Muqatta'at may be an ancient TABLE OF CONTENTS
""")
    else:
        print("""
FINDING: Muqatta'at groups do NOT show special thematic clustering.

This suggests:
- Section marking may not be thematic
- Or our similarity metric is too crude
- Or the grouping serves another purpose
""")

    # Additional analysis: Are consecutive surahs MORE similar?
    print("\n" + "=" * 60)
    print("BONUS: CONSECUTIVENESS ANALYSIS")
    print("=" * 60)

    # حم group is PERFECTLY consecutive (40-46)
    # Compare similarity of consecutive vs non-consecutive pairs

    ham_surahs = MUQATTAAT_GROUPS['حم']
    consecutive_pairs = []
    non_consecutive_pairs = []

    for i, s1 in enumerate(ham_surahs):
        for j, s2 in enumerate(ham_surahs[i+1:], i+1):
            sim = cosine_similarity(all_vocabs[s1], all_vocabs[s2])
            if abs(s1 - s2) == 1:  # Adjacent
                consecutive_pairs.append(sim)
            else:
                non_consecutive_pairs.append(sim)

    if consecutive_pairs and non_consecutive_pairs:
        cons_mean = sum(consecutive_pairs) / len(consecutive_pairs)
        nonc_mean = sum(non_consecutive_pairs) / len(non_consecutive_pairs)

        print(f"\nحم group (40-46):")
        print(f"  Adjacent pairs similarity: {cons_mean:.3f}")
        print(f"  Non-adjacent pairs similarity: {nonc_mean:.3f}")

        if cons_mean > nonc_mean * 1.1:
            print("  → Adjacent surahs are MORE similar (gradient structure)")
        else:
            print("  → No adjacency effect (uniform grouping)")

    # Save results
    with open('output/muqattaat_theme_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nResults saved to output/muqattaat_theme_analysis.json")

    return results


if __name__ == "__main__":
    main()

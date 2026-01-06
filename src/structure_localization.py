"""
STRUCTURE LOCALIZATION

Phase 1: WHERE does the cross-word structure live?

Experiments:
1.1 - Surah-level analysis (which surahs have most structure?)
1.2 - Meccan vs Medinan comparison
1.3 - Verse boundary test (does structure cross verses?)
"""

import sys
sys.path.insert(0, 'src')
import json
import random
import zlib
import time
from collections import defaultdict
from typing import List, Dict, Tuple

from encoding_functions.f_ordinal import encode_ordinal_5bit_abjad, extract_letters


# ============================================================
# UTILITIES
# ============================================================

class Progress:
    def __init__(self, total, desc=""):
        self.total = total
        self.current = 0
        self.desc = desc
        self.start = time.time()

    def update(self, n=1):
        self.current += n
        elapsed = time.time() - self.start
        pct = 100 * self.current / self.total
        rate = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / rate if rate > 0 else 0
        print(f"\r  [{self.desc}] {self.current}/{self.total} ({pct:.0f}%) ETA:{eta:.0f}s",
              end="", flush=True)

    def done(self):
        print(f"\r  [{self.desc}] DONE ({time.time()-self.start:.1f}s)" + " "*20)


def compress_ratio(bits: str) -> float:
    """Compression ratio using zlib."""
    if not bits or len(bits) < 10:
        return 1.0
    data = bits.encode()
    return len(zlib.compress(data, 9)) / len(data)


def word_permute(text: str, rng: random.Random) -> str:
    """Shuffle word order."""
    words = text.split()
    rng.shuffle(words)
    return ' '.join(words)


def verse_permute(verses: List[str], rng: random.Random) -> str:
    """Shuffle verse order, keep verses intact."""
    shuffled = verses.copy()
    rng.shuffle(shuffled)
    return ' '.join(shuffled)


def compute_structure_strength(text: str, encode_fn, n_perm: int = 30, seed: int = 42) -> Dict:
    """
    Compute structure strength: how much better does original compress vs shuffled?

    Returns dict with observed, null_mean, effect, p_value
    """
    if len(text.split()) < 10:  # Too short
        return {"observed": None, "null_mean": None, "effect": 0, "p_value": 1.0, "n_words": 0}

    bits = encode_fn(text)
    if len(bits) < 50:
        return {"observed": None, "null_mean": None, "effect": 0, "p_value": 1.0, "n_words": 0}

    observed = compress_ratio(bits)

    rng = random.Random(seed)
    null_dist = []
    for _ in range(n_perm):
        null_text = word_permute(text, rng)
        null_bits = encode_fn(null_text)
        null_dist.append(compress_ratio(null_bits))

    null_mean = sum(null_dist) / len(null_dist)
    effect = (null_mean - observed) * 8  # bits per char
    count_extreme = sum(1 for x in null_dist if x <= observed)
    p_value = (count_extreme + 1) / (n_perm + 1)

    return {
        "observed": observed,
        "null_mean": null_mean,
        "effect": effect,
        "p_value": p_value,
        "n_words": len(text.split()),
        "n_letters": len(extract_letters(text))
    }


# ============================================================
# EXPERIMENT 1.1: SURAH-LEVEL ANALYSIS
# ============================================================

def analyze_by_surah(data: List[Dict], n_perm: int = 30) -> List[Dict]:
    """
    Compute structure strength for each surah.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 1.1: SURAH-LEVEL ANALYSIS")
    print("="*60)

    results = []
    prog = Progress(len(data), "surahs")

    for surah in data:
        surah_text = ' '.join(v['text'] for v in surah['verses'])

        strength = compute_structure_strength(
            surah_text,
            encode_ordinal_5bit_abjad,
            n_perm=n_perm,
            seed=42 + surah['id']
        )

        results.append({
            "surah_id": surah['id'],
            "name": surah['name'],
            "name_en": surah['transliteration'],
            "type": surah['type'],  # meccan/medinan
            "n_verses": len(surah['verses']),
            **strength
        })
        prog.update()

    prog.done()

    # Sort by effect size
    results.sort(key=lambda x: x['effect'], reverse=True)

    print("\nTOP 10 SURAHS (most cross-word structure):")
    print("-" * 70)
    print(f"{'Rank':<5} {'Surah':<25} {'Type':<8} {'Verses':<7} {'Effect':<12} {'P-value':<10}")
    print("-" * 70)
    for i, r in enumerate(results[:10]):
        sig = "***" if r['p_value'] < 0.05 else ""
        print(f"{i+1:<5} {r['name_en']:<25} {r['type']:<8} {r['n_verses']:<7} "
              f"{r['effect']:.4f}{sig:<6} {r['p_value']:.3f}")

    print("\nBOTTOM 10 SURAHS (least cross-word structure):")
    print("-" * 70)
    for i, r in enumerate(results[-10:]):
        sig = "***" if r['p_value'] < 0.05 else ""
        print(f"{114-9+i:<5} {r['name_en']:<25} {r['type']:<8} {r['n_verses']:<7} "
              f"{r['effect']:.4f}{sig:<6} {r['p_value']:.3f}")

    return results


# ============================================================
# EXPERIMENT 1.2: MECCAN vs MEDINAN
# ============================================================

def analyze_meccan_vs_medinan(data: List[Dict], n_perm: int = 50) -> Dict:
    """
    Compare structure strength between Meccan and Medinan surahs.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 1.2: MECCAN vs MEDINAN")
    print("="*60)

    meccan_text = []
    medinan_text = []

    for surah in data:
        text = ' '.join(v['text'] for v in surah['verses'])
        if surah['type'] == 'meccan':
            meccan_text.append(text)
        else:
            medinan_text.append(text)

    meccan_full = ' '.join(meccan_text)
    medinan_full = ' '.join(medinan_text)

    print(f"\nMeccan: {len(meccan_text)} surahs, {len(meccan_full.split())} words")
    print(f"Medinan: {len(medinan_text)} surahs, {len(medinan_full.split())} words")

    print("\nAnalyzing Meccan surahs...")
    meccan_result = compute_structure_strength(meccan_full, encode_ordinal_5bit_abjad, n_perm)

    print("Analyzing Medinan surahs...")
    medinan_result = compute_structure_strength(medinan_full, encode_ordinal_5bit_abjad, n_perm)

    print("\nRESULTS:")
    print("-" * 50)
    print(f"{'Type':<10} {'Effect (bits/char)':<20} {'P-value':<10}")
    print("-" * 50)

    sig_m = "***" if meccan_result['p_value'] < 0.05 else ""
    sig_d = "***" if medinan_result['p_value'] < 0.05 else ""

    print(f"{'Meccan':<10} {meccan_result['effect']:<20.4f} {meccan_result['p_value']:.3f} {sig_m}")
    print(f"{'Medinan':<10} {medinan_result['effect']:<20.4f} {medinan_result['p_value']:.3f} {sig_d}")

    diff = meccan_result['effect'] - medinan_result['effect']
    print(f"\nDifference: {diff:+.4f} bits/char")
    if abs(diff) > 0.01:
        winner = "Meccan" if diff > 0 else "Medinan"
        print(f"→ {winner} surahs have MORE cross-word structure")
    else:
        print("→ No substantial difference")

    return {"meccan": meccan_result, "medinan": medinan_result}


# ============================================================
# EXPERIMENT 1.3: VERSE BOUNDARY TEST
# ============================================================

def analyze_verse_boundaries(data: List[Dict], n_perm: int = 50) -> Dict:
    """
    Test: Does structure cross verse boundaries?

    Compare:
    - Word shuffle (destroys all cross-word structure)
    - Verse shuffle (keeps within-verse, destroys cross-verse)

    If word_shuffle >> verse_shuffle → structure is mostly WITHIN verses
    If word_shuffle ≈ verse_shuffle → structure CROSSES verses
    """
    print("\n" + "="*60)
    print("EXPERIMENT 1.3: VERSE BOUNDARY TEST")
    print("="*60)
    print("\nQuestion: Does structure cross verse boundaries?")

    # Get all verses as list
    all_verses = []
    for surah in data:
        for verse in surah['verses']:
            all_verses.append(verse['text'])

    full_text = ' '.join(all_verses)

    print(f"\nTotal verses: {len(all_verses)}")
    print(f"Total words: {len(full_text.split())}")

    # Original compression
    bits = encode_ordinal_5bit_abjad(full_text)
    observed = compress_ratio(bits)
    print(f"\nOriginal compression: {observed:.4f}")

    # Word shuffle null
    print("\nComputing word-shuffle null...")
    rng = random.Random(42)
    word_null = []
    prog = Progress(n_perm, "word-perm")
    for _ in range(n_perm):
        null_text = word_permute(full_text, rng)
        null_bits = encode_ordinal_5bit_abjad(null_text)
        word_null.append(compress_ratio(null_bits))
        prog.update()
    prog.done()

    # Verse shuffle null
    print("Computing verse-shuffle null...")
    rng = random.Random(42)
    verse_null = []
    prog = Progress(n_perm, "verse-perm")
    for _ in range(n_perm):
        null_text = verse_permute(all_verses, rng)
        null_bits = encode_ordinal_5bit_abjad(null_text)
        verse_null.append(compress_ratio(null_bits))
        prog.update()
    prog.done()

    word_mean = sum(word_null) / len(word_null)
    verse_mean = sum(verse_null) / len(verse_null)

    effect_vs_word = (word_mean - observed) * 8
    effect_vs_verse = (verse_mean - observed) * 8

    # Structure breakdown
    within_verse = effect_vs_word - effect_vs_verse  # Destroyed by word but not verse
    cross_verse = effect_vs_verse  # Destroyed by verse shuffle

    print("\nRESULTS:")
    print("-" * 50)
    print(f"Original CR:        {observed:.4f}")
    print(f"Word-shuffle mean:  {word_mean:.4f}")
    print(f"Verse-shuffle mean: {verse_mean:.4f}")
    print("-" * 50)
    print(f"Total structure (vs word shuffle):  {effect_vs_word:.4f} bits/char")
    print(f"Cross-verse structure:              {cross_verse:.4f} bits/char ({100*cross_verse/effect_vs_word:.0f}%)")
    print(f"Within-verse structure:             {within_verse:.4f} bits/char ({100*within_verse/effect_vs_word:.0f}%)")

    print("\nINTERPRETATION:")
    if cross_verse > within_verse:
        print("→ MOST structure CROSSES verse boundaries")
        print("  (Verses are connected to each other)")
    elif within_verse > cross_verse * 2:
        print("→ MOST structure is WITHIN verses")
        print("  (Each verse is internally structured, but verses are independent)")
    else:
        print("→ Structure exists BOTH within and across verses")

    return {
        "observed": observed,
        "word_shuffle_mean": word_mean,
        "verse_shuffle_mean": verse_mean,
        "total_effect": effect_vs_word,
        "cross_verse_effect": cross_verse,
        "within_verse_effect": within_verse
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("STRUCTURE LOCALIZATION EXPERIMENTS")
    print("="*60)

    # Load data
    print("\nLoading Quran...")
    with open('data/quran/quran.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} surahs")

    # Run experiments
    results = {}

    # 1.1 Surah analysis (quick version)
    results['surah'] = analyze_by_surah(data, n_perm=20)

    # 1.2 Meccan vs Medinan
    results['period'] = analyze_meccan_vs_medinan(data, n_perm=30)

    # 1.3 Verse boundaries
    results['verse_boundary'] = analyze_verse_boundaries(data, n_perm=30)

    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)

    # Convert for JSON serialization
    output = {
        'surah_ranking': [
            {k: v for k, v in r.items() if k != 'name'}  # Remove Arabic for JSON
            for r in results['surah']
        ],
        'meccan_vs_medinan': {
            'meccan_effect': results['period']['meccan']['effect'],
            'medinan_effect': results['period']['medinan']['effect'],
        },
        'verse_boundary': results['verse_boundary']
    }

    with open('output/structure_localization.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Results saved to output/structure_localization.json")

    return results


if __name__ == "__main__":
    main()

"""
VERSE-LEVEL ENCODING ANALYSIS

Apply all encodings at verse granularity.
Output visualization-ready data in CSV and JSON formats.
"""

import sys
import json
import csv
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, shannon_entropy, compression_ratio,
    density, run_length_analysis
)
from research_loop import ALL_ENCODINGS, strip_diacritics, ABJAD


def analyze_verse(verse_text: str, surah_id: int, verse_id: int,
                  surah_name: str, surah_type: str) -> Dict[str, Any]:
    """Analyze a single verse with all encodings."""

    result = {
        'surah_id': surah_id,
        'verse_id': verse_id,
        'surah_name': surah_name,
        'surah_type': surah_type,
        'text_length': len(verse_text),
        'text_preview': verse_text[:100],
    }

    # Count letters
    clean = strip_diacritics(verse_text)
    arabic = re.compile(r'[\u0621-\u064A]')
    letters = [c for c in clean if arabic.match(c)]
    result['letter_count'] = len(letters)

    if len(letters) < 3:
        return None  # Skip very short verses

    # Apply each encoding
    for enc_name, enc_fn in ALL_ENCODINGS.items():
        bits = enc_fn(verse_text)
        if len(bits) < 3:
            result[f'{enc_name}_density'] = None
            result[f'{enc_name}_entropy'] = None
            result[f'{enc_name}_bitstring'] = ''
            continue

        d = density(bits)
        e = shannon_entropy(bits)
        runs = run_length_analysis(bits)

        result[f'{enc_name}_density'] = round(d, 4)
        result[f'{enc_name}_entropy'] = round(e, 4)
        result[f'{enc_name}_max_run_1'] = runs['max_1_run']
        result[f'{enc_name}_max_run_0'] = runs['max_0_run']
        result[f'{enc_name}_bitstring'] = bits

    return result


def analyze_all_verses(quran: List[Dict]) -> List[Dict]:
    """Analyze all verses in the Quran."""
    results = []

    for surah in quran:
        surah_id = surah['id']
        surah_name = surah['name']
        surah_type = surah.get('type', 'unknown')

        for verse in surah['verses']:
            verse_id = verse['id']
            verse_text = verse['text']

            result = analyze_verse(
                verse_text, surah_id, verse_id,
                surah_name, surah_type
            )

            if result:
                results.append(result)

    return results


def create_summary_stats(verse_data: List[Dict]) -> Dict[str, Any]:
    """Create summary statistics for visualization."""

    # Encoding names (excluding metadata)
    enc_names = [k.replace('_density', '') for k in verse_data[0].keys()
                 if k.endswith('_density')]

    summary = {
        'total_verses': len(verse_data),
        'encodings': [],
    }

    for enc in enc_names:
        densities = [v[f'{enc}_density'] for v in verse_data
                     if v.get(f'{enc}_density') is not None]

        if not densities:
            continue

        enc_stats = {
            'name': enc,
            'mean_density': round(sum(densities) / len(densities), 4),
            'min_density': round(min(densities), 4),
            'max_density': round(max(densities), 4),
            'std_density': round(
                (sum((d - sum(densities)/len(densities))**2 for d in densities) / len(densities))**0.5,
                4
            ),
        }

        # Distribution buckets (for histograms)
        buckets = [0] * 10  # 0-0.1, 0.1-0.2, ..., 0.9-1.0
        for d in densities:
            bucket = min(int(d * 10), 9)
            buckets[bucket] += 1
        enc_stats['distribution'] = buckets

        summary['encodings'].append(enc_stats)

    # Surah-level aggregation
    surah_stats = {}
    for v in verse_data:
        sid = v['surah_id']
        if sid not in surah_stats:
            surah_stats[sid] = {
                'surah_id': sid,
                'surah_name': v['surah_name'],
                'surah_type': v['surah_type'],
                'verse_count': 0,
                'total_letters': 0,
            }
            for enc in enc_names:
                surah_stats[sid][f'{enc}_densities'] = []

        surah_stats[sid]['verse_count'] += 1
        surah_stats[sid]['total_letters'] += v['letter_count']

        for enc in enc_names:
            d = v.get(f'{enc}_density')
            if d is not None:
                surah_stats[sid][f'{enc}_densities'].append(d)

    # Compute surah means
    surah_summary = []
    for sid, stats in surah_stats.items():
        surah_row = {
            'surah_id': stats['surah_id'],
            'surah_name': stats['surah_name'],
            'surah_type': stats['surah_type'],
            'verse_count': stats['verse_count'],
            'total_letters': stats['total_letters'],
        }
        for enc in enc_names:
            densities = stats[f'{enc}_densities']
            if densities:
                surah_row[f'{enc}_mean'] = round(sum(densities) / len(densities), 4)
        surah_summary.append(surah_row)

    summary['surah_stats'] = surah_summary

    return summary


def export_csv(verse_data: List[Dict], filepath: str):
    """Export verse data to CSV."""
    if not verse_data:
        return

    # Get all keys except bitstrings (too long)
    keys = [k for k in verse_data[0].keys() if not k.endswith('_bitstring')]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        for row in verse_data:
            writer.writerow({k: row.get(k) for k in keys})


def export_json(data: Any, filepath: str):
    """Export data to JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def main():
    """Main analysis."""
    print("VERSE-LEVEL ENCODING ANALYSIS")
    print("="*60)

    # Load data
    quran = load_quran("data/quran/quran.json")
    print(f"Loaded {len(quran)} surahs")

    # Analyze all verses
    print("Analyzing verses...")
    verse_data = analyze_all_verses(quran)
    print(f"Analyzed {len(verse_data)} verses")

    # Create summary
    print("Creating summary statistics...")
    summary = create_summary_stats(verse_data)

    # Export to CSV
    csv_path = "output/data/verses_encoded.csv"
    export_csv(verse_data, csv_path)
    print(f"Exported verse data to {csv_path}")

    # Export to JSON
    json_path = "output/data/verses_encoded.json"
    export_json(verse_data, json_path)
    print(f"Exported verse data to {json_path}")

    # Export summary
    summary_path = "output/data/encoding_summary.json"
    export_json(summary, summary_path)
    print(f"Exported summary to {summary_path}")

    # Export surah-level CSV
    surah_csv_path = "output/data/surahs_encoded.csv"
    if summary.get('surah_stats'):
        keys = list(summary['surah_stats'][0].keys())
        with open(surah_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(summary['surah_stats'])
        print(f"Exported surah data to {surah_csv_path}")

    # Print summary
    print("\n" + "="*60)
    print("ENCODING SUMMARY")
    print("="*60)
    print(f"\n{'Encoding':<20} {'Mean':<10} {'Min':<10} {'Max':<10} {'Std':<10}")
    print("-"*60)
    for enc in summary['encodings']:
        print(f"{enc['name']:<20} {enc['mean_density']:<10.4f} {enc['min_density']:<10.4f} "
              f"{enc['max_density']:<10.4f} {enc['std_density']:<10.4f}")

    return verse_data, summary


if __name__ == "__main__":
    main()

"""
SURAH-LEVEL ENCODING ANALYSIS

Analyze each of the 114 surahs.
Compare Meccan vs Medinan, short vs long, early vs late.
"""

import sys
import json
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import (
    load_quran, extract_text, shannon_entropy, compression_ratio,
    density, run_length_analysis, autocorrelation
)
from research_loop import ALL_ENCODINGS


def analyze_surah(surah: dict) -> dict:
    """Analyze a single surah with all encodings."""
    # Combine all verses
    full_text = ' '.join(v['text'] for v in surah['verses'])

    result = {
        'surah_id': surah['id'],
        'surah_name': surah['name'],
        'surah_name_transliteration': surah.get('transliteration', ''),
        'surah_type': surah.get('type', 'unknown'),
        'verse_count': surah.get('total_verses', len(surah['verses'])),
    }

    # Apply each encoding
    for enc_name, enc_fn in ALL_ENCODINGS.items():
        bits = enc_fn(full_text)
        if len(bits) < 10:
            continue

        result[f'{enc_name}_length'] = len(bits)
        result[f'{enc_name}_density'] = round(density(bits), 4)
        result[f'{enc_name}_entropy'] = round(shannon_entropy(bits), 4)
        result[f'{enc_name}_compression'] = round(compression_ratio(bits), 4)

        runs = run_length_analysis(bits)
        result[f'{enc_name}_max_run_1'] = runs['max_1_run']
        result[f'{enc_name}_max_run_0'] = runs['max_0_run']
        result[f'{enc_name}_total_runs'] = runs['total_runs']

    return result


def main():
    """Main analysis."""
    print("SURAH-LEVEL ENCODING ANALYSIS")
    print("="*70)

    # Load data
    quran = load_quran("data/quran/quran.json")
    print(f"Analyzing {len(quran)} surahs...")

    # Analyze each surah
    results = [analyze_surah(s) for s in quran]

    # Print summary table
    print("\n" + "="*70)
    print("SURAH SUMMARY (E8_solar encoding)")
    print("="*70)
    print(f"\n{'#':<4} {'Name':<15} {'Type':<8} {'Verses':<7} {'Density':<10} {'MaxRun1':<8} {'MaxRun0':<8}")
    print("-"*70)

    for r in results:
        print(f"{r['surah_id']:<4} {r['surah_name']:<15} {r['surah_type']:<8} "
              f"{r['verse_count']:<7} {r.get('E8_solar_density', 0):<10.4f} "
              f"{r.get('E8_solar_max_run_1', 0):<8} {r.get('E8_solar_max_run_0', 0):<8}")

    # Aggregate by type
    print("\n" + "="*70)
    print("MECCAN vs MEDINAN COMPARISON")
    print("="*70)

    meccan = [r for r in results if r['surah_type'] == 'meccan']
    medinan = [r for r in results if r['surah_type'] == 'medinan']

    encodings_to_compare = ['E1_dot', 'E2_voice', 'E4_throat', 'E8_solar']

    print(f"\n{'Encoding':<15} {'Meccan Mean':<15} {'Medinan Mean':<15} {'Difference':<15}")
    print("-"*60)

    for enc in encodings_to_compare:
        key = f'{enc}_density'
        meccan_vals = [r[key] for r in meccan if key in r]
        medinan_vals = [r[key] for r in medinan if key in r]

        m_mean = sum(meccan_vals) / len(meccan_vals) if meccan_vals else 0
        d_mean = sum(medinan_vals) / len(medinan_vals) if medinan_vals else 0
        diff = m_mean - d_mean

        print(f"{enc:<15} {m_mean:<15.4f} {d_mean:<15.4f} {diff:+.4f}")

    # Top and bottom surahs by density
    print("\n" + "="*70)
    print("TOP 10 SURAHS BY E8_SOLAR DENSITY")
    print("="*70)

    sorted_by_solar = sorted(results, key=lambda x: x.get('E8_solar_density', 0), reverse=True)

    print(f"\n{'#':<4} {'Name':<20} {'Type':<10} {'Density':<10}")
    print("-"*50)
    for r in sorted_by_solar[:10]:
        print(f"{r['surah_id']:<4} {r['surah_name']:<20} {r['surah_type']:<10} "
              f"{r.get('E8_solar_density', 0):.4f}")

    print("\n" + "="*70)
    print("BOTTOM 10 SURAHS BY E8_SOLAR DENSITY")
    print("="*70)

    print(f"\n{'#':<4} {'Name':<20} {'Type':<10} {'Density':<10}")
    print("-"*50)
    for r in sorted_by_solar[-10:]:
        print(f"{r['surah_id']:<4} {r['surah_name']:<20} {r['surah_type']:<10} "
              f"{r.get('E8_solar_density', 0):.4f}")

    # Extreme run lengths
    print("\n" + "="*70)
    print("LONGEST RUNS (E8_solar)")
    print("="*70)

    sorted_by_run1 = sorted(results, key=lambda x: x.get('E8_solar_max_run_1', 0), reverse=True)
    sorted_by_run0 = sorted(results, key=lambda x: x.get('E8_solar_max_run_0', 0), reverse=True)

    print("\nLongest Solar (1) Runs:")
    for r in sorted_by_run1[:5]:
        print(f"  Surah {r['surah_id']} ({r['surah_name']}): {r.get('E8_solar_max_run_1', 0)} consecutive")

    print("\nLongest Lunar (0) Runs:")
    for r in sorted_by_run0[:5]:
        print(f"  Surah {r['surah_id']} ({r['surah_name']}): {r.get('E8_solar_max_run_0', 0)} consecutive")

    # Export
    csv_path = "output/data/surahs_full_analysis.csv"
    keys = list(results[0].keys())
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nExported to {csv_path}")

    json_path = "output/data/surahs_full_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Exported to {json_path}")

    return results


if __name__ == "__main__":
    main()

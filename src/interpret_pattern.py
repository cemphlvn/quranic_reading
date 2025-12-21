"""
INTERPRET PATTERN

Now that we've established structure exists, we attempt interpretation.
Focus on E8_solar (strongest finding) and E4_throat.

Interpretation approaches:
1. Run-length analysis (what do long runs mean?)
2. Position analysis (where in verses do patterns cluster?)
3. Semantic correlation (do patterns correlate with meaning?)
4. Direct reading (what message does 1/0 sequence convey?)
"""

import sys
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from core.binary_analysis import load_quran, run_length_analysis
from research_loop import strip_diacritics


# Solar letters (assimilate with lam of definite article)
SOLAR = set('تثدذرزسشصضطظنل')
LUNAR = set('ابجحخعغفقكمهوي')


def encode_solar(text: str) -> str:
    """Solar=1, Lunar=0."""
    clean = strip_diacritics(text)
    bits = []
    for c in clean:
        if c in SOLAR:
            bits.append('1')
        elif c in LUNAR:
            bits.append('0')
    return ''.join(bits)


def analyze_by_verse(quran: list) -> dict:
    """Analyze patterns verse by verse."""
    results = []

    for surah in quran:
        for verse in surah['verses']:
            bits = encode_solar(verse['text'])
            if len(bits) < 5:
                continue

            density = bits.count('1') / len(bits)
            runs = run_length_analysis(bits)

            results.append({
                'surah': surah['id'],
                'verse': verse['id'],
                'text_preview': verse['text'][:50],
                'bitstring': bits[:50],
                'length': len(bits),
                'density': density,
                'max_run_1': runs['max_1_run'],
                'max_run_0': runs['max_0_run'],
            })

    return results


def find_extreme_verses(verse_data: list, n: int = 10):
    """Find verses with extreme density or run lengths."""
    # Highest solar density
    high_solar = sorted(verse_data, key=lambda x: -x['density'])[:n]

    # Lowest solar density (most lunar)
    low_solar = sorted(verse_data, key=lambda x: x['density'])[:n]

    # Longest solar run
    long_solar = sorted(verse_data, key=lambda x: -x['max_run_1'])[:n]

    # Longest lunar run
    long_lunar = sorted(verse_data, key=lambda x: -x['max_run_0'])[:n]

    return {
        'high_solar': high_solar,
        'low_solar': low_solar,
        'long_solar_run': long_solar,
        'long_lunar_run': long_lunar,
    }


def interpret_solar_lunar():
    """Semantic interpretation of solar/lunar pattern."""
    print("="*80)
    print("INTERPRETING E8_SOLAR (Solar/Lunar Letters)")
    print("="*80)

    print("""
BACKGROUND:
  Solar letters (حروف شمسية): ت ث د ذ ر ز س ش ص ض ط ظ ن ل
  Lunar letters (حروف قمرية): ا ب ج ح خ ع غ ف ق ك م ه و ي

  Named for how they interact with the definite article "ال":
  - Solar: The lam assimilates (الشمس = ash-shams, not al-shams)
  - Lunar: The lam is pronounced (القمر = al-qamar)

PHONETIC PROPERTIES:
  Solar letters are mostly coronal (tongue-tip) consonants.
  Lunar letters are mostly labial, velar, or pharyngeal.

SEMANTIC HYPOTHESIS:
  Solar (1) = manifest, active, apparent, external
  Lunar (0) = hidden, passive, internal, esoteric

  (This is speculative but follows the sun/moon metaphor)
""")

    # Load and analyze
    quran = load_quran("data/quran/quran.json")
    verse_data = analyze_by_verse(quran)

    print(f"\nAnalyzed {len(verse_data)} verses")

    # Find extremes
    extremes = find_extreme_verses(verse_data)

    # Report high solar density verses
    print("\n" + "-"*60)
    print("VERSES WITH HIGHEST SOLAR DENSITY (most 'manifest/active'):")
    print("-"*60)
    for v in extremes['high_solar'][:5]:
        print(f"\n  Surah {v['surah']}:{v['verse']} — density={v['density']:.2f}")
        print(f"  Bits: {v['bitstring']}")
        print(f"  Text: {v['text_preview']}...")

    # Report low solar density verses
    print("\n" + "-"*60)
    print("VERSES WITH LOWEST SOLAR DENSITY (most 'hidden/passive'):")
    print("-"*60)
    for v in extremes['low_solar'][:5]:
        print(f"\n  Surah {v['surah']}:{v['verse']} — density={v['density']:.2f}")
        print(f"  Bits: {v['bitstring']}")
        print(f"  Text: {v['text_preview']}...")

    # Report longest solar runs
    print("\n" + "-"*60)
    print("VERSES WITH LONGEST SOLAR RUNS (sustained 'manifest'):")
    print("-"*60)
    for v in extremes['long_solar_run'][:5]:
        print(f"\n  Surah {v['surah']}:{v['verse']} — max solar run={v['max_run_1']}")
        print(f"  Bits: {v['bitstring']}")
        print(f"  Text: {v['text_preview']}...")

    # Report longest lunar runs
    print("\n" + "-"*60)
    print("VERSES WITH LONGEST LUNAR RUNS (sustained 'hidden'):")
    print("-"*60)
    for v in extremes['long_lunar_run'][:5]:
        print(f"\n  Surah {v['surah']}:{v['verse']} — max lunar run={v['max_run_0']}")
        print(f"  Bits: {v['bitstring']}")
        print(f"  Text: {v['text_preview']}...")

    # Overall statistics
    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)

    densities = [v['density'] for v in verse_data]
    avg_density = sum(densities) / len(densities)
    print(f"\nMean solar density: {avg_density:.3f}")
    print(f"  (Solar letters are {avg_density*100:.1f}% of text)")

    # Density by surah type
    meccan = [v for v in verse_data if any(
        s['id'] == v['surah'] and s['type'] == 'meccan'
        for s in quran
    )]
    medinan = [v for v in verse_data if any(
        s['id'] == v['surah'] and s['type'] == 'medinan'
        for s in quran
    )]

    if meccan and medinan:
        meccan_density = sum(v['density'] for v in meccan) / len(meccan)
        medinan_density = sum(v['density'] for v in medinan) / len(medinan)
        print(f"\nMeccan surahs solar density: {meccan_density:.3f}")
        print(f"Medinan surahs solar density: {medinan_density:.3f}")

        if abs(meccan_density - medinan_density) > 0.01:
            if meccan_density > medinan_density:
                print("  → Meccan surahs are MORE solar (more manifest?)")
            else:
                print("  → Medinan surahs are MORE solar (more manifest?)")

    return verse_data, extremes


def main():
    """Main interpretation."""
    verse_data, extremes = interpret_solar_lunar()

    # Save data
    output = {
        'extremes': extremes,
        'sample_verses': verse_data[:100]
    }

    with open("projects/alpha/data/interpretation_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print("\nResults saved to projects/alpha/data/interpretation_results.json")


if __name__ == "__main__":
    main()

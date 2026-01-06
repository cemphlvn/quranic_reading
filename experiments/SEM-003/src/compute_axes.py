"""
SEM-003: Semantic Sentiment Axes

Project each ayah onto 6 interpretable semantic axes.
Uses embedded pole descriptions - no text matching needed.
"""

import os
import json
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM001_DATA = os.path.join(PROJECT_ROOT, 'experiments/SEM-001/output/data')


# =============================================================================
# AXIS DEFINITIONS - Arabic phrases that define each pole
# =============================================================================

AXES = {
    'threat_mercy': {
        'name': 'Threat ↔ Mercy',
        'negative': {
            'label': 'Threat',
            'phrases': [
                'عذاب شديد في نار جهنم',
                'هلاك القوم الظالمين',
                'عقاب أليم يوم القيامة',
                'خسران مبين في الآخرة',
                'سعير وحريق للكافرين',
            ]
        },
        'positive': {
            'label': 'Mercy',
            'phrases': [
                'رحمة الله ومغفرته',
                'جنات تجري من تحتها الأنهار',
                'هداية ونور وفلاح',
                'نعيم مقيم للمؤمنين',
                'فوز عظيم ورضوان',
            ]
        }
    },
    'narrative_normative': {
        'name': 'Narrative ↔ Normative',
        'negative': {
            'label': 'Narrative',
            'phrases': [
                'قال موسى لقومه',
                'قصة إبراهيم ونوح',
                'أرسلنا رسولا إلى فرعون',
                'نبأ الذين من قبلكم',
                'حديث الأنبياء والرسل',
            ]
        },
        'positive': {
            'label': 'Normative',
            'phrases': [
                'أقيموا الصلاة وآتوا الزكاة',
                'حرم عليكم الميتة والدم',
                'كتب عليكم الصيام',
                'أمر الله بالعدل والإحسان',
                'فريضة من الله حكيم عليم',
            ]
        }
    },
    'immanence_transcendence': {
        'name': 'Immanence ↔ Transcendence',
        'negative': {
            'label': 'Immanence',
            'phrases': [
                'الأرض والرزق والتجارة',
                'المال والأولاد والحياة الدنيا',
                'البيع والشراء والزرع',
                'الأنعام والحرث والثمار',
                'متاع الحياة الدنيا',
            ]
        },
        'positive': {
            'label': 'Transcendence',
            'phrases': [
                'الآخرة والملائكة والعرش',
                'الغيب والروح والقيامة',
                'الحساب والميزان والبعث',
                'السماوات العلى والملكوت',
                'عالم الغيب والشهادة',
            ]
        }
    },
    'intimacy_majesty': {
        'name': 'Intimacy ↔ Majesty',
        'negative': {
            'label': 'Intimacy',
            'phrases': [
                'يا أيها الذين آمنوا',
                'قل يا عبادي',
                'ربك الذي خلقك',
                'إياك نعبد وإياك نستعين',
                'ادعوني أستجب لكم',
            ]
        },
        'positive': {
            'label': 'Majesty',
            'phrases': [
                'خلق السماوات والأرض',
                'الملك القدوس العزيز الجبار',
                'رب العرش العظيم',
                'له ما في السماوات وما في الأرض',
                'الكبير المتعال',
            ]
        }
    },
    'certainty_contention': {
        'name': 'Certainty ↔ Contention',
        'negative': {
            'label': 'Certainty',
            'phrases': [
                'إن هذا لهو الحق المبين',
                'آمنوا بالله ورسوله',
                'علم اليقين والبينة',
                'الصدق والبرهان الواضح',
                'الحق من ربكم',
            ]
        },
        'positive': {
            'label': 'Contention',
            'phrases': [
                'يجادلون في آيات الله',
                'كذبوا وافتروا على الله',
                'أنكروا وشكوا وارتابوا',
                'خصومة المكذبين',
                'زعموا أنهم على الحق',
            ]
        }
    },
    'hope_fear': {
        'name': 'Hope ↔ Fear',
        'negative': {
            'label': 'Hope',
            'phrases': [
                'بشرى للمؤمنين',
                'الصبر والرجاء والأمل',
                'وعد الله الصالحين',
                'فرح وسرور وطمأنينة',
                'الخير والفوز في الآخرة',
            ]
        },
        'positive': {
            'label': 'Fear',
            'phrases': [
                'الساعة آتية بغتة',
                'خوف وفزع ورعب',
                'الحذر من عذاب عاجل',
                'هول يوم القيامة',
                'وجل القلوب من ذكر الله',
            ]
        }
    }
}


def load_embeddings():
    """Load ayah embeddings from SEM-001."""
    embeddings = np.load(os.path.join(SEM001_DATA, 'embeddings.npy'))
    with open(os.path.join(SEM001_DATA, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
    return embeddings, metadata


def embed_phrases(phrases: List[str]) -> np.ndarray:
    """Embed Arabic phrases using the same model as ayahs."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    return model.encode(phrases, convert_to_numpy=True)


def compute_axis_scores(
    ayah_embeddings: np.ndarray,
    neg_phrases: List[str],
    pos_phrases: List[str],
    phrase_embeddings_cache: Dict
) -> np.ndarray:
    """
    Compute axis scores for all ayahs.
    score = cos(ayah, C+) - cos(ayah, C-)
    """
    # Embed phrases (with caching)
    neg_key = tuple(neg_phrases)
    pos_key = tuple(pos_phrases)

    if neg_key not in phrase_embeddings_cache:
        phrase_embeddings_cache[neg_key] = embed_phrases(neg_phrases)
    if pos_key not in phrase_embeddings_cache:
        phrase_embeddings_cache[pos_key] = embed_phrases(pos_phrases)

    neg_embs = phrase_embeddings_cache[neg_key]
    pos_embs = phrase_embeddings_cache[pos_key]

    # Compute centroids
    neg_centroid = neg_embs.mean(axis=0)
    pos_centroid = pos_embs.mean(axis=0)

    # Compute similarities
    neg_sims = cosine_similarity(ayah_embeddings, [neg_centroid]).flatten()
    pos_sims = cosine_similarity(ayah_embeddings, [pos_centroid]).flatten()

    # Score = similarity to positive - similarity to negative
    scores = pos_sims - neg_sims

    return scores, neg_centroid, pos_centroid


def main():
    print("=" * 60)
    print("SEM-003: SEMANTIC SENTIMENT AXES")
    print("=" * 60)

    # Load ayah embeddings
    print("\nLoading ayah embeddings from SEM-001...")
    embeddings, metadata = load_embeddings()
    print(f"Loaded {len(embeddings)} ayahs")

    # Cache for phrase embeddings
    phrase_cache = {}

    # Process each axis
    all_scores = {}

    print("\nComputing axes (embedding pole phrases)...")
    for axis_id, axis_def in AXES.items():
        print(f"\n  {axis_def['name']}...")

        neg_phrases = axis_def['negative']['phrases']
        pos_phrases = axis_def['positive']['phrases']

        scores, neg_c, pos_c = compute_axis_scores(
            embeddings, neg_phrases, pos_phrases, phrase_cache
        )
        all_scores[axis_id] = scores

        # Stats
        print(f"    Range: [{scores.min():.3f}, {scores.max():.3f}]")
        print(f"    Mean: {scores.mean():.3f}, Std: {scores.std():.3f}")

    # Compute correlations between axes
    print("\n" + "=" * 60)
    print("AXIS CORRELATIONS")
    print("=" * 60)

    axis_ids = list(all_scores.keys())
    score_matrix = np.array([all_scores[aid] for aid in axis_ids])
    corr = np.corrcoef(score_matrix)

    print("\n" + " " * 12 + "  ".join([f"{aid[:6]:>6}" for aid in axis_ids]))
    for i, aid in enumerate(axis_ids):
        row = "  ".join([f"{corr[i,j]:>6.2f}" for j in range(len(axis_ids))])
        print(f"{aid[:12]:12} {row}")

    # Meccan vs Medinan comparison
    print("\n" + "=" * 60)
    print("MECCAN vs MEDINAN")
    print("=" * 60)

    meccan_idx = [i for i, m in enumerate(metadata) if m['type'] == 'meccan']
    medinan_idx = [i for i, m in enumerate(metadata) if m['type'] == 'medinan']

    for axis_id in axis_ids:
        scores = all_scores[axis_id]
        meccan_mean = scores[meccan_idx].mean()
        medinan_mean = scores[medinan_idx].mean()
        diff = medinan_mean - meccan_mean
        print(f"  {AXES[axis_id]['name']:30} Meccan: {meccan_mean:+.3f}  Medinan: {medinan_mean:+.3f}  Δ: {diff:+.3f}")

    # Save outputs
    output_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')
    os.makedirs(output_dir, exist_ok=True)

    # Save scores per ayah
    scores_per_ayah = []
    for i in range(len(embeddings)):
        entry = {
            'idx': i,
            'surah_id': metadata[i]['surah_id'],
            'verse_id': metadata[i]['verse_id'],
            'surah_name': metadata[i]['surah_name'],
            'type': metadata[i]['type'],
        }
        for axis_id in all_scores:
            entry[axis_id] = float(all_scores[axis_id][i])
        scores_per_ayah.append(entry)

    with open(os.path.join(output_dir, 'axis_scores.json'), 'w') as f:
        json.dump(scores_per_ayah, f, indent=2)

    # Save correlation matrix
    np.save(os.path.join(output_dir, 'axis_correlations.npy'), corr)

    print(f"\nSaved to {output_dir}/")
    print("\nDone! Next: run visualize.py")


if __name__ == "__main__":
    main()

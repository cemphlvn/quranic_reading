"""
SEM-001: Quran Semantic Embeddings

Generate embeddings for all 6,236 ayahs using Arabic language models.
"""

import sys
import os
import json
import numpy as np
from typing import List, Dict, Tuple

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EXPERIMENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

# Model options (in order of preference)
MODELS = [
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",  # Good multilingual baseline
    "aubmindlab/bert-base-arabertv02",  # Arabic-specific
    "asafaya/bert-base-arabic",  # Another Arabic option
]


def load_quran() -> List[Dict]:
    """Load Quran and return list of ayahs with metadata."""
    with open(os.path.join(PROJECT_ROOT, 'data/quran/quran.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    ayahs = []
    for surah in data:
        for verse in surah['verses']:
            ayahs.append({
                'surah_id': surah['id'],
                'surah_name': surah['transliteration'],
                'surah_name_ar': surah['name'],
                'verse_id': verse['id'],
                'text': verse['text'],
                'type': surah['type'],  # meccan/medinan
            })

    return ayahs


def get_embeddings_transformer(texts: List[str], model_name: str, batch_size: int = 32) -> np.ndarray:
    """Generate embeddings using sentence-transformers."""
    from sentence_transformers import SentenceTransformer

    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)

    print(f"Generating embeddings for {len(texts)} texts...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


def get_embeddings_arabert(texts: List[str], batch_size: int = 16) -> np.ndarray:
    """Generate embeddings using AraBERT with mean pooling."""
    from transformers import AutoTokenizer, AutoModel
    import torch

    model_name = "aubmindlab/bert-base-arabertv02"
    print(f"Loading model: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    embeddings = []

    print(f"Generating embeddings for {len(texts)} texts...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]

        # Tokenize
        encoded = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)

        # Get embeddings
        with torch.no_grad():
            outputs = model(**encoded)
            # Mean pooling over tokens
            attention_mask = encoded['attention_mask']
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            batch_embeddings = (sum_embeddings / sum_mask).cpu().numpy()

        embeddings.append(batch_embeddings)

        if (i // batch_size) % 10 == 0:
            print(f"  Processed {min(i+batch_size, len(texts))}/{len(texts)}")

    return np.vstack(embeddings)


def compute_similarity_matrix(embeddings: np.ndarray, top_k: int = 50) -> Dict:
    """
    Compute sparse similarity matrix (top-k neighbors per node).

    Returns dict mapping node_id -> [(neighbor_id, similarity), ...]
    """
    from sklearn.metrics.pairwise import cosine_similarity

    n = len(embeddings)
    print(f"Computing similarities for {n} ayahs...")

    # Compute in chunks to manage memory
    chunk_size = 500
    neighbors = {}

    for i in range(0, n, chunk_size):
        end_i = min(i + chunk_size, n)
        chunk = embeddings[i:end_i]

        # Similarity of chunk against all
        sims = cosine_similarity(chunk, embeddings)

        for j, row in enumerate(sims):
            node_id = i + j
            # Get top-k (excluding self)
            row[node_id] = -1  # Exclude self
            top_indices = np.argsort(row)[-top_k:][::-1]
            top_sims = row[top_indices]

            neighbors[node_id] = [
                (int(idx), float(sim))
                for idx, sim in zip(top_indices, top_sims)
                if sim > 0
            ]

        print(f"  Processed {end_i}/{n}")

    return neighbors


def main():
    print("=" * 60)
    print("SEM-001: QURAN SEMANTIC EMBEDDINGS")
    print("=" * 60)

    # Load data
    print("\nLoading Quran...")
    ayahs = load_quran()
    print(f"Loaded {len(ayahs)} ayahs")

    texts = [a['text'] for a in ayahs]

    # Try to generate embeddings
    try:
        # Try sentence-transformers first (easier)
        embeddings = get_embeddings_transformer(
            texts,
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )
    except ImportError:
        print("\nsentence-transformers not installed. Install with:")
        print("  pip install sentence-transformers")
        return
    except Exception as e:
        print(f"\nError with sentence-transformers: {e}")
        print("Trying AraBERT...")
        try:
            embeddings = get_embeddings_arabert(texts)
        except ImportError:
            print("\ntransformers not installed. Install with:")
            print("  pip install transformers torch")
            return

    print(f"\nEmbedding shape: {embeddings.shape}")

    # Save embeddings
    output_dir = os.path.join(EXPERIMENT_ROOT, 'output/data')

    np.save(os.path.join(output_dir, 'embeddings.npy'), embeddings)
    print(f"Saved embeddings to {output_dir}/embeddings.npy")

    # Save metadata
    metadata = [{
        'idx': i,
        'surah_id': a['surah_id'],
        'verse_id': a['verse_id'],
        'surah_name': a['surah_name'],
        'type': a['type']
    } for i, a in enumerate(ayahs)]

    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {output_dir}/metadata.json")

    # Compute sparse similarity
    print("\nComputing similarity graph...")
    neighbors = compute_similarity_matrix(embeddings, top_k=20)

    with open(os.path.join(output_dir, 'neighbors.json'), 'w') as f:
        json.dump(neighbors, f)
    print(f"Saved neighbor graph to {output_dir}/neighbors.json")

    # Quick stats
    print("\n" + "=" * 60)
    print("QUICK STATS")
    print("=" * 60)

    # Average similarity to nearest neighbor
    avg_top1 = np.mean([neighbors[i][0][1] for i in range(len(ayahs)) if neighbors[i]])
    print(f"Average similarity to nearest neighbor: {avg_top1:.3f}")

    # Check if sequential ayahs are similar
    sequential_sims = []
    for i in range(len(ayahs) - 1):
        # Find similarity to next ayah
        for neighbor_id, sim in neighbors[i]:
            if neighbor_id == i + 1:
                sequential_sims.append(sim)
                break

    if sequential_sims:
        print(f"Average similarity to NEXT ayah: {np.mean(sequential_sims):.3f}")
        print(f"(vs random neighbor would be ~{avg_top1:.3f})")

    print("\nDone! Next: run graph_analysis.py")


if __name__ == "__main__":
    main()

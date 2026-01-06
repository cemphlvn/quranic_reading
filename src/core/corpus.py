"""
CORPUS MANAGEMENT

Infrastructure for cross-corpus comparison.
Required for any claims about Quran-specific structure.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Corpus:
    """A text corpus for comparison."""
    name: str
    description: str
    text: str
    source: str
    language: str


# Corpus registry
CORPORA: Dict[str, Corpus] = {}


def register_corpus(name: str, description: str, text: str, source: str, language: str = "Arabic"):
    """Register a corpus for comparison."""
    CORPORA[name] = Corpus(name, description, text, source, language)


def load_quran_corpus() -> Corpus:
    """Load Quran as a corpus."""
    from core.binary_analysis import load_quran, extract_text
    quran = load_quran("data/quran/quran.json")
    text = extract_text(quran, "full")
    return Corpus(
        name="quran",
        description="Quran (Uthmani script)",
        text=text,
        source="data/quran/quran.json",
        language="Classical Arabic"
    )


def get_corpus(name: str) -> Optional[Corpus]:
    """Get a corpus by name."""
    if name == "quran":
        return load_quran_corpus()
    return CORPORA.get(name)


def list_corpora() -> List[str]:
    """List all available corpora."""
    return ["quran"] + list(CORPORA.keys())


def add_corpus_from_file(name: str, filepath: str, description: str):
    """Add a corpus from a text file."""
    text = Path(filepath).read_text(encoding='utf-8')
    register_corpus(name, description, text, filepath)


def add_corpus_from_text(name: str, text: str, description: str):
    """Add a corpus from raw text."""
    register_corpus(name, description, text, "inline", "Arabic")


# ============================================================
# PLACEHOLDER CORPORA (to be populated with real data)
# ============================================================

PLACEHOLDER_NOTE = """
IMPORTANT: These are placeholder entries.
To make valid cross-corpus claims, you must:
1. Obtain actual classical Arabic texts
2. Add them using add_corpus_from_file()
3. Re-run hypothesis tests

Without real comparison corpora, NO claims about
Quran-specific structure are valid.
"""


def init_placeholder_corpora():
    """Initialize placeholder entries for required comparison corpora."""
    # These are placeholders - need real data
    required_corpora = [
        ("pre_islamic_poetry", "Pre-Islamic Arabic poetry (Mu'allaqat, etc.)"),
        ("classical_prose", "Classical Arabic prose (various sources)"),
        ("hadith", "Hadith collections (Bukhari, Muslim, etc.)"),
        ("modern_arabic", "Modern Standard Arabic (news, literature)"),
    ]

    for name, desc in required_corpora:
        if name not in CORPORA:
            register_corpus(
                name,
                f"[PLACEHOLDER] {desc}",
                "",  # Empty text - must be populated
                "PLACEHOLDER - ADD REAL DATA",
                "Arabic"
            )


init_placeholder_corpora()


# ============================================================
# CROSS-CORPUS TESTING
# ============================================================

def compare_encoding_across_corpora(
    encoding_name: str,
    encode_fn,
    corpus_names: List[str] = None
) -> Dict[str, Dict]:
    """
    Apply encoding to multiple corpora and compare.

    This is required for any "Quran-specific" claims.
    """
    from core.statistics import compression_ratio, compression_all

    if corpus_names is None:
        corpus_names = list_corpora()

    results = {}
    for name in corpus_names:
        corpus = get_corpus(name)
        if corpus is None or not corpus.text:
            results[name] = {"error": "Corpus not available or empty"}
            continue

        bits = encode_fn(corpus.text)
        results[name] = {
            "corpus": name,
            "text_length": len(corpus.text),
            "bitstring_length": len(bits),
            "density": bits.count('1') / len(bits) if bits else 0,
            "compression": compression_all(bits) if bits else {},
        }

    return results

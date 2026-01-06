"""
NULL MODELS

Proper null hypothesis generators for binary encoding analysis.
Each null model preserves different statistical properties.
"""

import random
import re
from typing import List, Callable


def null_random_shuffle(bits: str) -> str:
    """
    N1: Random shuffle.
    Preserves: 0/1 ratio only
    Destroys: All sequential structure
    """
    b = list(bits)
    random.shuffle(b)
    return ''.join(b)


def null_block_shuffle(bits: str, block_size: int = 20) -> str:
    """
    N3: Block shuffle.
    Preserves: Local patterns within blocks
    Destroys: Long-range structure
    """
    blocks = [bits[i:i+block_size] for i in range(0, len(bits), block_size)]
    random.shuffle(blocks)
    return ''.join(blocks)


def null_markov_surrogate(bits: str) -> str:
    """
    N4: Markov surrogate.
    Preserves: 1-rate and transition probabilities P(b|prev)
    Destroys: Higher-order structure

    This is the critical test: does structure exceed first-order Markov?
    """
    if len(bits) < 2:
        return bits

    # Count transitions
    transitions = {'0': {'0': 0, '1': 0}, '1': {'0': 0, '1': 0}}
    for i in range(len(bits) - 1):
        transitions[bits[i]][bits[i+1]] += 1

    # Convert to probabilities
    probs = {}
    for prev in ['0', '1']:
        total = transitions[prev]['0'] + transitions[prev]['1']
        if total > 0:
            probs[prev] = transitions[prev]['1'] / total
        else:
            probs[prev] = 0.5

    # Generate surrogate
    result = [bits[0]]  # Start with same first bit
    for _ in range(len(bits) - 1):
        prev = result[-1]
        if random.random() < probs[prev]:
            result.append('1')
        else:
            result.append('0')

    return ''.join(result)


def null_word_permutation(text: str, encode_fn: Callable) -> str:
    """
    N5: Word permutation.
    Preserves: Within-word encoding structure
    Destroys: Cross-word structure

    This is the correct test for "beyond word boundaries".
    """
    # Extract Arabic words
    words = re.findall(r'[\u0621-\u064A\u0617-\u061A\u064B-\u0652]+', text)
    if len(words) < 2:
        return encode_fn(text)

    # Shuffle word order
    random.shuffle(words)

    # Re-encode the permuted text
    permuted_text = ' '.join(words)
    return encode_fn(permuted_text)


def get_transition_matrix(bits: str) -> dict:
    """Get transition probability matrix for analysis."""
    if len(bits) < 2:
        return {'0->0': 0.5, '0->1': 0.5, '1->0': 0.5, '1->1': 0.5}

    counts = {'00': 0, '01': 0, '10': 0, '11': 0}
    for i in range(len(bits) - 1):
        counts[bits[i] + bits[i+1]] += 1

    total_0 = counts['00'] + counts['01']
    total_1 = counts['10'] + counts['11']

    return {
        '0->0': counts['00'] / total_0 if total_0 > 0 else 0.5,
        '0->1': counts['01'] / total_0 if total_0 > 0 else 0.5,
        '1->0': counts['10'] / total_1 if total_1 > 0 else 0.5,
        '1->1': counts['11'] / total_1 if total_1 > 0 else 0.5,
    }


# Registry of null models
NULL_MODELS = {
    'random': null_random_shuffle,
    'block_10': lambda b: null_block_shuffle(b, 10),
    'block_20': lambda b: null_block_shuffle(b, 20),
    'block_50': lambda b: null_block_shuffle(b, 50),
    'markov': null_markov_surrogate,
}

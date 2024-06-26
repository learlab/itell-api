"""
Deprecated. No longer in use.
"""

from gensim.models.doc2vec import Doc2Vec
from scipy import spatial
import numpy as np

doc2vec_mod = Doc2Vec.load("assets/doc2vec-model")


def semantic_similarity(source_tokens: list[str], summary_tokens: list[str]) -> float:
    """Return semantic similarity score based on summary and source text"""
    source_embed: np.ndarray = doc2vec_mod.infer_vector(source_tokens)  # type: ignore
    summary_embed: np.ndarray = doc2vec_mod.infer_vector(summary_tokens)  # type: ignore

    cosine = spatial.distance.cosine(summary_embed, source_embed)

    return np.subtract(1, cosine)

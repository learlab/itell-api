from sentence_transformers import SentenceTransformer
from scipy import spatial
import numpy as np


class EmbeddingPipeline:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = SentenceTransformer(self.model_name)

    def __call__(self, text_input: str) -> list[float]:
        embed = self.model.encode(text_input)
        if not isinstance(embed, np.ndarray):
            raise TypeError(f"Expected np.ndarray, got {type(embed)}")
        return embed.tolist()

    def score_similarity(self, a: str, b: str) -> float:
        """Return semantic similarity score based on summary and source text"""
        a_embed = self.model.encode(a)
        b_embed = self.model.encode(b)

        cosine = spatial.distance.cosine(a_embed, b_embed)

        return np.subtract(1, cosine)

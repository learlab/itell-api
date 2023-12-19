from sentence_transformers import SentenceTransformer
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
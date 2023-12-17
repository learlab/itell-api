from sentence_transformers import SentenceTransformer
from torch import Tensor


class EmbeddingPipeline:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = SentenceTransformer(self.model_name)

    def __call__(self, text_input: str) -> list[float]:
        tensor = self.model.encode(text_input)
        if not isinstance(tensor, Tensor):
            raise TypeError(f"Expected Tensor, got {type(tensor)}")
        return tensor.tolist()

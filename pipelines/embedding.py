from sentence_transformers import SentenceTransformer


class EmbeddingPipeline:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = SentenceTransformer(self.model_name)

    def __call__(self, text_input: str) -> list[float]:
        return self.model.encode(text_input).tolist()

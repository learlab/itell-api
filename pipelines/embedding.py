from sentence_transformers import SentenceTransformer
from supabase.client import Client


class EmbeddingPipeline(object):
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = SentenceTransformer(self.model_name)

    def __call__(self, text_input: str) -> list[float]:
        return self.model.encode(text_input).tolist()

    def retrieve_chunks(
        self,
        text_input: str,
        db: Client,
        match_threshold: float = 0.3,
        match_count: int = 3,
    ) -> list[dict]:
        embedding = self(text_input)
        results = db.rpc(
            "retrieve_chunks",
            {
                "embedding": embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
            },
        ).execute()

        return results.data

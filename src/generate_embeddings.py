from pipelines.embedding import EmbeddingPipeline
from models.embedding import ChunkInput, ChunkEmbedding
from supabase.client import Client

embedding_pipeline = EmbeddingPipeline()


async def generate_embedding(input_body: ChunkInput) -> ChunkEmbedding:
    embed = embedding_pipeline(input_body.text)
    return ChunkEmbedding(embed=embed)


# def max_similarity(text_input: str, db: Client) -> float:
#     return embedding_pipeline.max_similarity(text_input, db)


def retrieve_chunks(
    text_input: str,
    db: Client,
    match_threshold: float = 0.3,
    match_count: int = 1,
) -> list[dict]:
    results = embedding_pipeline.retrieve_chunks(
        text_input, db, match_threshold, match_count
    )
    return results

from supabase.client import Client
from typing import Any

from pipelines.embedding import EmbeddingPipeline
from models.embedding import ChunkInput, ChunkEmbedding

embedding_pipeline = EmbeddingPipeline()


async def generate_embedding(input_body: ChunkInput) -> ChunkEmbedding:
    embed = embedding_pipeline(input_body.text)
    return ChunkEmbedding(embed=embed)


async def retrieve_chunks(
    text_input: str,
    db: Client,
    match_threshold: float = 0.3,
    match_count: int = 1,
) -> list[dict[str, Any]]:
    embed = embedding_pipeline(text_input)
    results = db.rpc(
        "retrieve_chunks",
        {
            "embedding": embed,
            "match_threshold": match_threshold,
            "match_count": match_count,
        },
    ).execute()
    return results.data

from supabase.client import Client
from typing import Any
from database import get_vector_store

from pipelines.embed import EmbeddingPipeline
from models.embedding import ChunkInput, RetrievalInput, RetrievalResults

embedding_pipeline = EmbeddingPipeline()
db = get_vector_store()

async def generate_embedding(input_body: ChunkInput) -> dict[str, Any]:
    embed = embedding_pipeline(input_body['content'])
    upsert_response = db.embeddings.upsert({
        "text": input_body['text'],
        "module": input_body['module'],
        "chapter": input_body['chapter'],
        "page": input_body['page'],
        "chunk": input_body['chunk'],
        "content": input_body['content'],
        "embedding": embedding
    })

    if upsert_response.error:
        return {'content' : {'message' : response.error}, 'status_code': 500}
    else:
        return {'content' : {'message' : response.data}, 'status_code': 200}
    return None

async def retrieve_chunks(input_body: RetrievalInput, match_threshold: float = 0.3, match_count: int = 1) -> RetrievalResults:
    content_embedding = embedding_pipeline(input_body['content'])
    results = db.rpc(
        "retrieve_chunks",
        {
            "embedding": content_embedding,
            "text": input_body["text"],
            "page": input_body["page"],
            "match_threshold": match_threshold,
            "match_count": match_count,
        },
    ).execute()

    return results.data
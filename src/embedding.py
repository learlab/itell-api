from typing import Any
from src.database import get_vector_store

from pipelines.embed import EmbeddingPipeline
from models.embedding import ChunkInput, RetrievalInput, RetrievalResults

embedding_pipeline = EmbeddingPipeline()
db = get_vector_store()

async def generate_embedding(input_body: ChunkInput) -> dict[str, Any]:
    embedding = embedding_pipeline(input_body['content'])
    try:
        upsert_response = db.table("embeddings").upsert({
            "text": input_body['text'],
            "module": input_body['module'],
            "chapter": input_body['chapter'],
            "page": input_body['page'],
            "chunk": input_body['chunk'],
            "content": input_body['content'],
            "embedding": embedding
        }).execute()
        return {'content' : {'message' : upsert_response.data}, 'status_code': 201}
    except Exception as ex:
        return {'content' : {'message' : ex.message}, 'status_code': ex.code}

async def retrieve_chunks(input_body: RetrievalInput, match_threshold: float = 0.3, match_count: int = 2) -> RetrievalResults:
    content_embedding = embedding_pipeline(input_body['content'])
    try:
        query_params = {
            "embedding": content_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
        }
        if 'text' in input_body:
            query_params['text'] = input_body["text"]
        if 'page' in input_body:
            query_params['page'] = input_body["page"]
                
        results = db.rpc("retrieve_chunks", query_params).execute()
        return results.data
    except Exception as ex:
        return [{'content' : {'message' : ex.message}, 'status_code': ex.code}]
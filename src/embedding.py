from fastapi import Response, HTTPException

from connections.vectorstore import get_vector_store

from pipelines.embed import EmbeddingPipeline
from models.embedding import ChunkInput, RetrievalInput, RetrievalResults

embedding_pipeline = EmbeddingPipeline()
db = get_vector_store()


async def embedding_generate(input_body: ChunkInput) -> Response:
    embedding = embedding_pipeline(input_body.content)
    upsert_response = (
        db.table("embeddings")
        .upsert(
            {
                "text": input_body.text_slug,
                "module": input_body.module_slug,
                "chapter": input_body.chapter_slug,
                "page": input_body.page_slug,
                "chunk": input_body.chunk_slug,
                "content": input_body.content,
                "embedding": embedding,
            }
        )
        .execute()
    )
    return Response(content=upsert_response.data[0]["content"], status_code=201)


async def chunks_retrieve(input_body: RetrievalInput) -> RetrievalResults:
    content_embedding = embedding_pipeline(input_body.text)
    query_params = {
        "embedding": content_embedding,
        "match_threshold": input_body.similarity_threshold,
        "match_count": input_body.match_count,
        "page": input_body.page_slug,
    }

    try:
        matches = db.rpc("retrieve_chunks", query_params).execute().data
    except (TypeError, AttributeError) as error:
        raise HTTPException(status_code=500, detail=str(error))

    return RetrievalResults(matches=matches)

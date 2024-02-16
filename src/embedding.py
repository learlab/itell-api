from .connections.vectorstore import get_vector_store
from .pipelines.embed import EmbeddingPipeline
from .models.embedding import ChunkInput, RetrievalInput, RetrievalResults

from fastapi import Response, HTTPException

embedding_pipeline = EmbeddingPipeline()


async def embedding_generate(input_body: ChunkInput) -> Response:
    db = get_vector_store()

    embedding = embedding_pipeline(input_body.content)[0].tolist()
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
    db = get_vector_store()

    content_embedding = embedding_pipeline(input_body.text)[0].tolist()
    query_params = {
        "embedding": content_embedding,
        "match_threshold": input_body.similarity_threshold,
        "match_count": input_body.match_count,
        "retrieve_strategy": input_body.retrieve_strategy,
        "page": input_body.page_slug,
    }

    try:
        matches = db.rpc("retrieve_chunks", query_params).execute().data
    except (TypeError, AttributeError) as error:
        raise HTTPException(status_code=500, detail=str(error))

    return RetrievalResults(matches=matches)


async def page_similarity(embedding: list[float], page_slug: str) -> float:
    db = get_vector_store()
    query_params = {
        "summary_embedding": embedding,
        "target_page": page_slug,
    }
    try:
        similarity = (
            db.rpc("page_similarity", query_params).execute().data[0]["similarity"]
        )
    except (TypeError, AttributeError) as error:
        raise HTTPException(status_code=500, detail=str(error))
    
    if similarity is None:
        raise HTTPException(status_code=404, detail="Page not found in Vector Store")

    return similarity

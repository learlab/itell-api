from .connections.vectorstore import get_vector_store
from .pipelines.embed import EmbeddingPipeline
from .models.embedding import (
    ChunkInput,
    RetrievalInput,
    RetrievalResults,
    DeleteUnusedInput,
)

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
        "embed": content_embedding,
        "match_threshold": input_body.similarity_threshold,
        "match_count": input_body.match_count,
        "retrieve_strategy": input_body.retrieve_strategy,
        "page_slugs": input_body.page_slugs,
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
        message = f"Page similarity not found for {page_slug}"
        raise HTTPException(status_code=404, detail=message)

    return similarity


async def delete_unused(input_body: DeleteUnusedInput) -> Response:
    # Deletes all chunks not in the chunk slugs list
    db = get_vector_store()

    current_slugs = (
        db.table("embeddings")
        .select("chunk")
        .eq("page", input_body.page_slug)
        .execute()
        .data
    )

    # Get all chunks in current_slugs not in input_body.chunk_slugs
    unused_slugs = [
        chunk["chunk"]
        for chunk in current_slugs
        if chunk["chunk"] not in input_body.chunk_slugs
    ]

    if unused_slugs:
        db.table("embeddings").delete().in_("chunk", unused_slugs).execute()

    return Response(status_code=202)

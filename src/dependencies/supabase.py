from fastapi import HTTPException, Response
from supabase.client import AsyncClient

from ..models.embedding import (ChunkInput, DeleteUnusedInput, RetrievalInput,
                                RetrievalResults)
from ..pipelines.embed import EmbeddingPipeline


class SupabaseClient(AsyncClient):
    """Supabase client with custom methods for embedding and retrieval.
    Caching is not possible since each embedding will be different.
    Could improve performance by creating a local copy of the relatively small
    vector store and querying that instead of the remote database."""

    embedding_pipeline = EmbeddingPipeline()

    async def embed(self, text: str) -> list[float]:
        return self.embedding_pipeline(text)[0].tolist()

    async def embedding_generate(self, input_body: ChunkInput) -> Response:

        embedding = await self.embed(input_body.content)

        upsert_response = (
            await self.table("embeddings")
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

    async def retrieve_chunks(self, input_body: RetrievalInput) -> RetrievalResults:

        embedding = await self.embed(input_body.text)

        query_params = {
            "embed": embedding,
            "match_threshold": input_body.similarity_threshold,
            "match_count": input_body.match_count,
            "retrieve_strategy": input_body.retrieve_strategy,
            "page_slugs": input_body.page_slugs,
        }

        try:
            response = await self.rpc("retrieve_chunks", query_params).execute()
        except (TypeError, AttributeError) as error:
            raise HTTPException(status_code=500, detail=str(error))

        matches = response.data

        return RetrievalResults(matches=matches)

    async def page_similarity(self, embedding: list[float], page_slug: str) -> float:
        """Returns the similarity between the embedding and the target page."""

        query_params = {
            "summary_embedding": embedding,
            "target_page": page_slug,
        }

        try:
            response = await self.rpc("page_similarity", query_params).execute()
        except (TypeError, AttributeError) as error:
            raise HTTPException(status_code=500, detail=str(error))

        similarity = response.data[0]["similarity"]

        if similarity is None:
            message = f"Page similarity not found for {page_slug}"
            raise HTTPException(status_code=404, detail=message)

        return similarity

    async def delete_unused(self, input_body: DeleteUnusedInput) -> Response:
        """Deletes all chunks not in the chunk slugs list."""

        response = (
            await self.table("embeddings")
            .select("chunk")
            .eq("page", input_body.page_slug)
            .execute()
        )

        current_slugs = response.data

        # Get all chunks in current_slugs not in input_body.chunk_slugs
        unused_slugs = [
            chunk["chunk"]
            for chunk in current_slugs
            if chunk["chunk"] not in input_body.chunk_slugs
        ]

        if unused_slugs:
            (
                await self.table("embeddings")
                .delete()
                .in_("chunk", unused_slugs)
                .execute()
            )

        return Response(status_code=202)

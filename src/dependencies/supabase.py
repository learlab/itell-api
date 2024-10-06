from fastapi import HTTPException, Response
from pydantic import ValidationError
from supabase.client import AsyncClient

from ..pipelines.embed import EmbeddingPipeline
from ..schemas.embedding import ChunkInput, DeleteUnusedInput
from ..schemas.prior import VolumePrior


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

        await (
            self.table("embeddings")
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

        return Response(status_code=201)

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

    async def get_volume_prior(self, volume_slug: str) -> VolumePrior:

        response = (
            await self.table("volume_priors")
            .select("*")
            .eq("slug", volume_slug)
            .execute()
        )

        # Default prior if none exists
        if not response.data:
            return VolumePrior(
                slug=volume_slug,
                mean=0.2,
                support=15,
                alpha=3.5,
                beta=4.0,
            )
        else:
            try:
                prior = VolumePrior(**response.data[0])
            except ValidationError as error:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to parse volume prior for {volume_slug}. {error}",
                )

            return prior

    async def update_volume_prior(self, prior: VolumePrior) -> Response:
        """Updates the volume prior for a given volume."""

        await (
            self.table("volume_priors")
            .upsert(
                prior.model_dump(),
                on_conflict="slug",  # Triggers an update if the slug already exists
            )
            .execute()
        )

        return Response(status_code=201)

    async def reset_volume_prior(self, volume_slug: str) -> Response:
        """Resets the volume prior for a given volume."""

        await (
            self.table("volume_priors")
            .update(
                {
                    "mean": 0.2,
                    "support": 15,
                    "alpha": 3.5,
                    "beta": 4.0,
                }
            )
            .eq("slug", volume_slug)
            .execute()
        )

        return Response(status_code=201)

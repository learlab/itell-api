from ..models.transcript import TranscriptInput, TranscriptResults
from ..models.embedding import (
    ChunkInput,
    RetrievalInput,
    RetrievalResults,
    DeleteUnusedInput,
)

from ..transcript import transcript_generate
from ..embedding import embedding_generate, chunks_retrieve, delete_unused

from fastapi import APIRouter, HTTPException, Response
from .logging_router import LoggingRoute

router = APIRouter(route_class=LoggingRoute)


@router.post("/generate/question")
async def generate_question(input_body: ChunkInput) -> None:
    """Not implemented."""
    raise HTTPException(status_code=404, detail="Not Implemented")


@router.post("/generate/keyphrases")
async def generate_keyphrases() -> None:
    """Not implemented."""
    raise HTTPException(status_code=404, detail="Not Implemented")


@router.post("/generate/transcript")
async def generate_transcript(input_body: TranscriptInput) -> TranscriptResults:
    """Generate a transcript from a YouTube video.
    Intended for use by the Content Management System."""
    return await transcript_generate(input_body)


@router.post("/generate/embedding")
async def generate_embedding(input_body: ChunkInput) -> Response:
    """This endpoint generates an embedding for a provided chunk of text
    and saves it to the vector store on SupaBase.
    It is only intended to be called by the Content Management System.
    """
    return await embedding_generate(input_body)


@router.post("/retrieve/chunks")
async def retrieve_chunks(input_body: RetrievalInput) -> RetrievalResults:
    return await chunks_retrieve(input_body)


@router.post("/delete/embedding")
async def delete_unused_chunks(input_body: DeleteUnusedInput) -> Response:
    """This endpoint accepts a list of slugs of chunks currently in STRAPI.
    It deletes any embeddings in the vector store that are not in the list.
    """
    return await delete_unused(input_body)

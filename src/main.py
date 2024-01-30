from .models.summary import (
    SummaryInputStrapi,
    SummaryInputSupaBase,
    SummaryResults,
    StreamingSummaryResults,
)
from .models.answer import AnswerInputStrapi, AnswerInputSupaBase, AnswerResults
from .models.embedding import ChunkInput, RetrievalInput, RetrievalResults
from .models.chat import ChatInput, PromptInput
from .models.message import Message
from .models.transcript import TranscriptInput, TranscriptResults
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Response
from typing import Union, AsyncGenerator

from .sert import sert_generate
from .summary_eval_supabase import summary_score_supabase
from .summary_eval import summary_score
from .summary_feedback import get_feedback
from .answer_eval_supabase import answer_score_supabase
from .answer_eval import answer_score
from .transcript import transcript_generate

import os
import json
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

description = """
Welcome to iTELL AI, a REST API for intelligent textbooks.
iTELL AI provides the following principal features:

- Summary scoring
- Constructed response item scoring
- Structured dialogues with conversational AI

iTELL AI also provides some utility endpoints
that are used by the content management system.
- Generating transcripts from YouTube videos
- Creating chunk embeddings and managing a vector store.
"""

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
    # Samples 100% of transactions. We should decrease this value in the future.
    profiles_sample_rate=1.0,
)


app = FastAPI(
    title="iTELL AI",
    description=description,
    summary="AI for intelligent textbooks",
    version="0.0.2",
    contact={
        "name": "LEAR Lab",
        "url": "https://learlab.org/contact",
        "email": "lear.lab.vu@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello() -> Message:
    return Message(message="This is a summary scoring API for iTELL.")


@app.post("/score/summary")
async def score_summary(
    input_body: Union[SummaryInputStrapi, SummaryInputSupaBase]
) -> SummaryResults:
    """Score a summary.
    Requires a textbook name if the textbook content is on SupaBase.
    Requires a page_slug if the textbook content is in our Strapi CMS.
    """
    if isinstance(input_body, SummaryInputSupaBase):
        return await summary_score_supabase(input_body)
    else:  # Strapi method
        _, results = await summary_score(input_body)
        return results


@app.post("/score/answer")
async def score_answer(
    input_body: Union[AnswerInputStrapi, AnswerInputSupaBase]
) -> AnswerResults:
    """Score a constructed response item.
    Requires a textbook name and location IDs if the textbook content is on SupaBase.
    Requires a page_slug and chunk_slug if the textbook content is in our Strapi CMS.
    """
    if isinstance(input_body, AnswerInputSupaBase):
        return await answer_score_supabase(input_body)
    else:  # Strapi method
        return await answer_score(input_body)


@app.post("/generate/question")
async def generate_question(input_body: ChunkInput) -> None:
    raise HTTPException(status_code=404, detail="Not Implemented")


@app.post("/generate/keyphrases")
async def generate_keyphrases(input_body: ChunkInput) -> None:
    raise HTTPException(status_code=404, detail="Not Implemented")


@app.post("/generate/transcript")
async def generate_transcript(input_body: TranscriptInput) -> TranscriptResults:
    return await transcript_generate(input_body)


if not os.environ.get("ENV") == "development":
    import torch
    from src.embedding import embedding_generate, chunks_retrieve
    from src.chat import moderated_chat, unmoderated_chat

    @app.get("/gpu", description="Check if GPU is available.")
    def gpu_is_available() -> Message:
        if torch.cuda.is_available():
            return Message(message="GPU is available.")
        else:
            return Message(message="GPU is not available.")

    @app.post("/chat")
    async def chat(input_body: ChatInput) -> StreamingResponse:
        """Responds to user queries incorporating relevant chunks from the current page.

        The response is a StreamingResponse wih the following fields:
        - **request_id**: a unique identifier for the request
        - **text**: the response text
        """
        return StreamingResponse(await moderated_chat(input_body))

    @app.post("/chat/raw")
    async def raw_chat(input_body: PromptInput) -> StreamingResponse:
        """Direct access to the underlying chat model.
        For testing purposes.
        """
        return StreamingResponse(await unmoderated_chat(input_body))

    @app.post("/score/summary/stairs", response_model=StreamingSummaryResults)
    async def score_summary_with_stairs(
        input_body: SummaryInputStrapi,
    ) -> StreamingResponse:
        """Scores a summary. If the summary fails, selects a chunk for re-reading and
        generates a self-explanation (SERT) question about the chunk.

        The response is a stream of Server-Sent Events (SSEs). The first response will
        be a SummaryResults object with additional fields for feedback.

        If the summary fails, subsequent responses will be:
        - **request_id**: a unique identifier for the request
        - **text**: the self-explanation question text
        - **chunk**: the slug of the chunk selected for re-reading
        - **question_type**: the type of SERT question
        """
        summary, results = await summary_score(input_body)
        feedback = get_feedback(results)
        stream = await sert_generate(summary)

        async def stream_results() -> AsyncGenerator[bytes, None]:
            yield (json.dumps(feedback.dict()) + "\0").encode("utf-8")
            async for ret in stream:
                yield ret

        return StreamingResponse(stream_results())

    @app.post("/generate/embedding")
    async def generate_embedding(input_body: ChunkInput) -> Response:
        return await embedding_generate(input_body)

    @app.post("/retrieve/chunks")
    async def retrieve_chunks(input_body: RetrievalInput) -> RetrievalResults:
        return await chunks_retrieve(input_body)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=False
    )

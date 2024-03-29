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
from typing import Union, AsyncGenerator, Callable

from fastapi.responses import StreamingResponse
from fastapi import (
    FastAPI,
    HTTPException,
    Response,
    Request,
    BackgroundTasks,
    APIRouter,
)
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware

from .summary_eval_supabase import summary_score_supabase
from .summary_eval import summary_score
from .summary_feedback import get_feedback
from .answer_eval_supabase import answer_score_supabase
from .answer_eval import answer_score
from .transcript import transcript_generate

import os
import sentry_sdk
from starlette.background import BackgroundTask
import uuid
import logging


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
    environment=os.environ.get("ENV"),
    traces_sample_rate=1.0,
    profiles_sample_rate=0.1,  # 10% of transactions
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

logging.basicConfig(level=logging.DEBUG)


def log_info(req: str, resp: str) -> None:
    idem = str(uuid.uuid4())
    logging.info(f"REQUEST  {idem}: {req}")
    logging.info(f"RESPONSE {idem}: {resp}")


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()
            response = await original_route_handler(request)
            existing_task = response.background

            if isinstance(response, StreamingResponse):
                task = BackgroundTask(log_info, req_body.decode(), "streaming response")
            else:
                task = BackgroundTask(
                    log_info, req_body.decode(), response.body.decode()
                )

            # check if the original response had a background task assigned to it
            if existing_task:
                response.background = BackgroundTasks(tasks=[existing_task, task])
            else:
                response.background = task

            return response

        return custom_route_handler


router = APIRouter(route_class=LoggingRoute)


@router.get("/")
def hello() -> Message:
    """Welcome to iTELL AI!"""
    return Message(message="This is a summary scoring API for iTELL.")


@router.post("/score/summary")
async def score_summary(
    input_body: Union[SummaryInputStrapi, SummaryInputSupaBase],
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


@router.post("/score/answer")
async def score_answer(
    input_body: Union[AnswerInputStrapi, AnswerInputSupaBase],
) -> AnswerResults:
    """Score a constructed response item.
    Requires a textbook name and location IDs if the textbook content is on SupaBase.
    Requires a page_slug and chunk_slug if the textbook content is in our Strapi CMS.
    """
    if isinstance(input_body, AnswerInputSupaBase):
        return await answer_score_supabase(input_body)
    else:  # Strapi method
        return await answer_score(input_body)


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


if not os.environ.get("ENV") == "development":
    import torch
    from src.embedding import embedding_generate, chunks_retrieve
    from src.chat import moderated_chat, unmoderated_chat
    from .sert import sert_generate

    @router.get("/gpu", description="Check if GPU is available.")
    def gpu_is_available() -> Message:
        """Check if GPU is available."""
        if torch.cuda.is_available():
            return Message(message="GPU is available.")
        else:
            return Message(message="GPU is not available.")

    @router.post("/chat")
    async def chat(input_body: ChatInput) -> StreamingResponse:
        """Responds to user queries incorporating relevant chunks from the current page.

        The response is a StreamingResponse wih the following fields:
        - **request_id**: a unique identifier for the request
        - **text**: the response text
        """
        return StreamingResponse(await moderated_chat(input_body))

    @router.post("/chat/raw")
    async def raw_chat(input_body: PromptInput) -> StreamingResponse:
        """Direct access to the underlying chat model.
        For testing purposes.
        """
        return StreamingResponse(await unmoderated_chat(input_body))

    @router.post("/score/summary/stairs", response_model=StreamingSummaryResults)
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
            yield (feedback.model_dump_json() + "\0").encode("utf-8")
            async for ret in stream:
                yield ret

        return StreamingResponse(stream_results())

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


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=False
    )

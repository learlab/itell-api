from .models.summary import (
    SummaryInputStrapi,
    SummaryResults,
    StreamingSummaryResults,
)
from .models.answer import AnswerInputStrapi, AnswerResults
from .models.embedding import (
    ChunkInput,
    RetrievalInput,
    RetrievalResults,
    DeleteUnusedInput,
)
from .models.chat import ChatInput, PromptInput, ChatInputCRI
from .models.message import Message
from .models.transcript import TranscriptInput, TranscriptResults
from .chat import language_feedback_chat
from typing import AsyncGenerator, Callable

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

from .summary_eval import summary_score
from .summary_feedback import get_feedback
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
    profiles_sample_rate=0.05,  # Log 5% of transactions
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

logging.basicConfig(level=logging.WARNING)


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
    input_body: SummaryInputStrapi,
) -> SummaryResults:
    """Score a summary.
    Requires a page_slug.
    """
    _, results = await summary_score(input_body)
    return results


@router.post("/score/answer")
async def score_answer(
    input_body: AnswerInputStrapi,
) -> AnswerResults:
    """Score a constructed response item.
    Requires a page_slug and chunk_slug.
    """
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
    from src.embedding import embedding_generate, chunks_retrieve, delete_unused
    from src.chat import moderated_chat, unmoderated_chat, cri_chat
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

    @router.post("/chat/CRI")
    async def chat_cri(input_body: ChatInputCRI) -> StreamingResponse:
        """Explains why a student's response to a constructed response item
        was evaluated as incorrect
        """
        return StreamingResponse(await cri_chat(input_body))

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
        # current setup - always generates a SERT question
        stream = await sert_generate(summary)

        ### ================================================== ###
        ### This is where the triggers for STAIRS should go ###
        ## e.g.

        # for item in feedback.prompt_details:
        #     if item.type == "Wording":
        #         wording = item
        #     elif item.type == "Content":
        #         content = item

        # if not content.feedback.is_passed:
        #     stream = await sert_generate(summary)
        # elif not wording.feedback.is_passed:
        #     stream = await language_feedback_chat(summary)
        # else:
        #     stream = False
        ### ================================================== ###

        async def stream_results() -> AsyncGenerator[bytes, None]:
            yield f"event: summaryfeedback\ndata: {feedback.model_dump_json()}\n\n"
            if stream:
                async for ret in stream:
                    yield ret

        return StreamingResponse(
            content=stream_results(), media_type="text/event-stream"
        )

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


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=False
    )

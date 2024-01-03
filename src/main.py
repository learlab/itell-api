from .models.summary import SummaryInputStrapi, SummaryInputSupaBase, SummaryResults
from .models.answer import AnswerInputStrapi, AnswerInputSupaBase, AnswerResults
from .models.embedding import ChunkInput, RetrievalInput, RetrievalResults
from .models.chat import ChatInput, ChatResult
from .models.message import Message
from .models.transcript import TranscriptInput, TranscriptResults
from .summary_eval_supabase import summary_score_supabase
from .summary_eval import summary_score
from .answer_eval_supabase import answer_score_supabase
from .answer_eval import answer_score
from .transcript import transcript_generate

import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from typing import Union

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
    dsn="https://d8e406671b4ca30dcecb4d7c4e0a9b0c@o4506435193405440.ingest.sentry.io/4506435194650624",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello() -> Message:
    return Message(message="This is a summary scoring API for iTELL.")


@app.get("/sentry-debug", description="Raises a ZeroDivisionError when called.")
async def trigger_error():
    return 1 / 0


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
        return await summary_score(input_body)


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
    from src.chat import moderated_chat

    @app.get("/gpu", description="Check if GPU is available.")
    def gpu_is_available() -> Message:
        if torch.cuda.is_available():
            return Message(message="GPU is available.")
        else:
            return Message(message="GPU is not available.")

    @app.post("/chat")
    async def chat(input_body: ChatInput) -> ChatResult:
        return ChatResult(await moderated_chat(input_body))

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

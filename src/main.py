import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .models.summary import SummaryInput, SummaryResults
from .models.answer import AnswerInput, AnswerResults
from .models.embedding import ChunkInput, RetrievalInput, RetrievalResults
from .models.chat import ChatInput, ChatResult
from .models.transcript import TranscriptInput, TranscriptResults

from .summary_eval_supabase import summary_score_supabase
from .summary_eval import summary_score
from .answer_eval_supabase import answer_score_supabase
from .answer_eval import answer_score
from .transcript import transcript_generate

description = """
Welcome to iTELL AI, a REST API for intelligent textbooks. iTELL AI provides the following principal features:

- Summary scoring
- Constructed response item scoring
- Structured dialogues with conversational AI

iTELL AI also provides some utility endpoints that are used by the content management system. 
- Generating transcripts from YouTube videos
- Creating chunk embeddings and managing a vector store.
"""

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


origins = [
    "*",
    # TODO: Remove wildcard. Add authentication methods.
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://textbook-demo.web.app",
    "https://itell.vercel.app",
    "https://itell-poe.vercel.app",
    "https://itell-think-python.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    return {"message": "This is a summary scoring API for iTELL."}


@app.get("/gpu", description="Check if GPU is available.")
def gpu() -> dict[str, str | bool]:
    if os.environ.get("ENV") == "development":
        return {"message": "Not available in development mode."}
    else:
        import torch

        return {"message": torch.cuda.is_available()}


@app.post("/score/summary")
async def score_summary(input_body: SummaryInput) -> SummaryResults:
    """Score a summary.
    Requires a textbook name if the textbook content is on SupaBase.
    Requires a page_slug if the textbook content is in our Strapi CMS.
    """
    input_body = SummaryInput.parse_obj(input_body)
    if input_body.textbook_name:  # supabase requires textbook_name (deprecated)
        return await summary_score_supabase(input_body)
    else:
        return await summary_score(input_body)


@app.post("/score/answer")
async def score_answer(input_body: AnswerInput) -> AnswerResults:
    """Score a constructed response item.
    Requires a textbook name and location IDs if the textbook content is on SupaBase.
    Requires a page_slug and chunk_slug if the textbook content is in our Strapi CMS.
    """
    if input_body.textbook_name:  # supabase requires textbook_name (deprecated)
        return await answer_score_supabase(input_body)
    else:  # Strapi method
        return await answer_score(input_body)


@app.post("/generate/question")
async def gen_question(input_body: ChunkInput) -> None:
    raise HTTPException(status_code=404, detail="Not Implemented")


@app.post("/generate/keyphrases")
async def gen_keyphrases(input_body: ChunkInput) -> None:
    raise HTTPException(status_code=404, detail="Not Implemented")


@app.post("/generate/transcript")
async def generate_transcript(input_body: TranscriptInput) -> TranscriptResults:
    return await transcript_generate(input_body)


if os.environ.get("ENV") == "development":
    print("Skipping chat/embedding endpoints in development mode.")
else:
    from src.embedding import embedding_generate, chunks_retrieve
    from src.chat import moderated_chat

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

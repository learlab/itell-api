import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from models.summary import SummaryInput, SummaryResults
from models.answer import AnswerInput, AnswerResults
from models.embedding import ChunkInput
from models.chat import ChatInput, ChatResult
from models.transcript import TranscriptInput, TranscriptResults

from src.summary_eval_supabase import summary_score_supabase
from src.summary_eval import summary_score_strapi
from src.answer_eval_supabase import answer_score_supabase
from src.answer_eval import answer_score
from src.embedding import generate_embedding
from src.get_transcript import generate_transcript

app = FastAPI()

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


@app.get("/gpu")
def gpu_available():
    import torch

    return {"message": f"GPU Available: {torch.cuda.is_available()}"}


@app.post("/score/summary")
async def score_summary(input_body: SummaryInput) -> SummaryResults:
    if input_body.textbook_name:
        return await summary_score_strapi(input_body)
    else:
        return await summary_score(input_body)


@app.post("/score/answer")
async def score_answer(input_body: AnswerInput) -> AnswerResults:
    if input_body.textbook_name:
        return await answer_score_supabase(input_body)
    else:
        return await answer_score(input_body)


@app.post("/generate/embedding")
async def gen_embedding(input_body: ChunkInput) -> Response:
    return await generate_embedding(input_body)


@app.post("/generate/question")
async def gen_question(input_body: ChunkInput) -> None:
    raise HTTPException(status_code=404, detail="Not Implemented")


@app.post("/generate/keyphrases")
async def gen_keyphrases(input_body: ChunkInput) -> None:
    raise HTTPException(status_code=404, detail="Not Implemented")


@app.post("/generate/transcript")
async def gen_transcript(input_body: TranscriptInput) -> TranscriptResults:
    return await generate_transcript(input_body)

if os.environ.get("ENV") == "development":
    print("Skipping chat endpoint in development mode.")
else:
    from src.chat import moderated_chat

    @app.post("/chat")
    async def chat(input_body: ChatInput) -> ChatResult:
        return ChatResult(await moderated_chat(input_body))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=False
    )

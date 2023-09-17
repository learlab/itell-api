import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.summary import SummaryInput, SummaryResults
from models.answer import AnswerInput, AnswerResults
from models.embedding import ChunkInput, ChunkEmbedding
from models.chat import ChatInput, ChatResult

from src.summary_eval import summary_score
from src.answer_eval import answer_score
from src.generate_embeddings import generate_embedding
from src.chat import moderated_chat

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
    return await summary_score(input_body)


@app.post("/score/answer")
async def score_answer(input_body: AnswerInput) -> AnswerResults:
    return await answer_score(input_body)


@app.post("/embed")
async def embed(input_body: ChunkInput) -> ChunkEmbedding:
    return await generate_embedding(input_body)


@app.post("/chat")
async def chat(input_body: ChatInput) -> ChatResult:
    return await moderated_chat(input_body)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=True
    )

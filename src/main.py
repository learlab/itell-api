import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.summary import SummaryInput, SummaryResults
from models.answer import AnswerInput, AnswerResults

from summary_eval import summary_score
from answer_eval import answer_score

app = FastAPI()

origins = [
    "*",
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
def score_summary(input_body: SummaryInput) -> SummaryResults:
    return summary_score(input_body)


@app.post("/score/answer")
def score_answer(input_body: AnswerInput) -> AnswerResults:
    return answer_score(input_body)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=True
    )

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.summary import SummaryInput, SummaryResults
from models.answer import AnswerInput, AnswerResults

from summary_eval import summary_score
from answer_eval import answer_score

from typing import Union
from enum import Enum


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


class ScoreType(str, Enum):
    summary = "summary"
    answer = "answer"


@app.get("/")
def hello():
    return {"message": "This is a summary scoring API for iTELL."}


@app.get("/gpu")
def gpu_available():
    import torch

    return {"message": f"GPU Available: {torch.cuda.is_available()}"}


@app.post("/score/{score_type}")
def score(
    score_type: ScoreType, input_body: Union[SummaryInput, AnswerInput]
) -> Union[SummaryResults, AnswerResults]:
    if score_type == ScoreType.summary:
        return summary_score(input_body)

    elif score_type == ScoreType.answer:
        return answer_score(input_body)

    else:
        raise HTTPException(status_code=404, detail="Invalid score type")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        reload=True
    )

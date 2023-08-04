import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.summary import SummaryInput, SummaryResults
from models.QA import QAInput, QAResults

from summary_eval import summary_score
from qa_eval import qa_score

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


@app.post("/score")
def score(summary_input: SummaryInput) -> SummaryResults:
    return summary_score(summary_input)


@app.post("/qascore")
def qascore(qa_input: QAInput) -> QAResults:
    return qa_score(qa_input)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        reload=True
    )

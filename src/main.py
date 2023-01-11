import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.summary import SummaryInput, SummaryResults
from summary_eval import summary_score

app = FastAPI()

origins = [
    "http://localhost:8000",
    "https://textbook-demo.web.app",
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
    return {"message": "Hello World"}


@app.post("/score")
def score(summary_input: SummaryInput) -> SummaryResults:
    return summary_score(summary_input)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8001)), reload=True
    )

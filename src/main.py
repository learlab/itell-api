import os

from fastapi import FastAPI

from models.summary import SummaryInput, SummaryResults
from src.summary_eval import get_score
from utils import containment_score
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    return {"message": "Hello World"}

@app.post("/score")
def score(summary_input: SummaryInput) -> SummaryResults:
    '''Scores a summary in the following sequence. If the summary scores below a threshold at any step,
    stop processing and return.
    '''
    results = SummaryResults(
        containment=containment_score(summary_input)
        )

    if results.containment > 0.6:
        results.score = 0
    else:
        results.score = get_score(summary_input)

    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True
    )

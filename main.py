import os

from fastapi import FastAPI

from src.summaryEval import get_score
from src.utils import containment_score
from src.models.summary import SummaryInput, SummaryResults

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World"}

@app.post("/score")
def score(summary_input: SummaryInput) -> SummaryResults:
    results = SummaryResults(containment = containment_score(summary_input))

    if results.containment > .6:
        results.score = 0
    else:
        results.score = get_score(summary_input)

    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True
    )

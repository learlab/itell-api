import os

from fastapi import FastAPI

from src.model import get_score
from src.utils import containment_score
from src.models.summary import SummaryInput

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World"}

@app.post("/score")
def score(summary_input: SummaryInput):
#     overlap = containment_score(summary_input.text)
#     if overlap > .6:
#         return {"score": 0, "containment": containment}
#     else:
    return {"score": get_score(summary_input.text)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True
    )

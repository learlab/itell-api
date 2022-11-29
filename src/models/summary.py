from pydantic import BaseModel


class SummaryInput(BaseModel):
    source: str
    text: str


class SummaryResults(BaseModel):
    score: float | None = None  # deprecated!
    content: float | None = None
    wording: float | None = None
    containment: float | None = None

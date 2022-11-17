from pydantic import BaseModel

class SummaryInput(BaseModel):
    text: str
    source: str

class SummaryResults(BaseModel):
    score: float # deprecated!
    content: float
    wording: float
    containment: float

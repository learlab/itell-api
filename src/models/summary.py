from pydantic import BaseModel, constr
from typing import Optional

class SummaryInput(BaseModel):
    section_number: constr(regex=r'^\d+-\d+$') # constrain string to chapter-section format "10-1"
    source: Optional[str]
    summary: str


class SummaryResults(BaseModel):
    content: float | None = None
    wording: float | None = None
    containment: float | None = None
    similarity: float | None = None

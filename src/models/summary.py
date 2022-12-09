from pydantic import BaseModel
from typing import Optional

class SummaryInput(BaseModel):
    textbook_name: Optional[str]
    chapter_index: int
    section_index: int
    source: Optional[str]
    summary: str


class SummaryResults(BaseModel):
    content: float | None = None
    wording: float | None = None
    containment: float | None = None
    similarity: float | None = None

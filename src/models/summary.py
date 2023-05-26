from pydantic import BaseModel
from typing import Optional


class SummaryInput(BaseModel):
    textbook_name: Optional[str]
    chapter_index: int
    section_index: int
    source: Optional[str]
    summary: str


class SummaryResults(BaseModel):
    containment: float
    similarity: float
    profanity: bool
    included_keyphrases: set[str]
    suggested_keyphrases: set[str]
    content: float | None = None
    wording: float | None = None

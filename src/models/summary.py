from pydantic import BaseModel
from typing import Optional
from models.textbook import TextbookNames


class SummaryInput(BaseModel):
    textbook_name: TextbookNames
    chapter_index: Optional[int] = 00
    section_index: Optional[int] = 00
    source: Optional[str] = None
    summary: str


class SummaryResults(BaseModel):
    containment: float
    similarity: float
    profanity: bool
    included_keyphrases: set[str]
    suggested_keyphrases: set[str]
    content: Optional[float] = None
    wording: Optional[float] = None

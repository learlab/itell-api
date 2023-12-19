from .textbook import TextbookNames
from typing import Optional, Dict, Set
from pydantic import BaseModel


class SummaryInputStrapi(BaseModel):
    page_slug: str
    summary: str
    focus_time: Dict[str, int] = dict()  # {"chunk_slug": "seconds", ...}


class SummaryInputSupaBase(BaseModel):
    textbook_name: TextbookNames
    chapter_index: int
    section_index: Optional[int] = None
    summary: str
    focus_time: Dict[str, int] = dict()  # {"chunk_slug": "seconds", ...}


class SummaryResults(BaseModel):
    containment: float
    similarity: float
    english: bool
    included_keyphrases: Set[str]
    suggested_keyphrases: Set[str]
    content: Optional[float] = None
    wording: Optional[float] = None

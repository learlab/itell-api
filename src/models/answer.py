from pydantic import BaseModel
from .textbook import TextbookNames
from typing import Optional


class AnswerInputStrapi(BaseModel):
    page_slug: str
    chunk_slug: str
    answer: str


class AnswerInputSupaBase(BaseModel):
    textbook_name: TextbookNames
    chapter_index: int
    section_index: Optional[int] = None
    subsection_index: int
    answer: str


class AnswerResults(BaseModel):
    score: float  # BLEURT or some other score
    is_passing: bool

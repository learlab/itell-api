from pydantic import BaseModel
from typing import Optional
from models.textbook import TextbookNames


class AnswerInput(BaseModel):
    textbook_name: TextbookNames
    chapter_index: Optional[int] = 00
    section_index: Optional[int] = 00
    subsection_index: int  # QAs are going to have to need subsection info
    answer: str


class AnswerResults(BaseModel):
    score: float  # BLEURT or some other score
    is_passing: bool

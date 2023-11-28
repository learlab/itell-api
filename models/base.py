from pydantic import BaseModel
from typing import Optional
from models.textbook import TextbookNames


class InputBase(BaseModel):
    textbook_name: Optional[TextbookNames] = None
    page_slug: Optional[str] = None
    chunk_slug: Optional[str] = None
    chapter_index: Optional[int] = 0
    section_index: Optional[int] = 0
    subsection_index: Optional[int] = 0


class ResultsBase(BaseModel):
    pass

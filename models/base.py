from pydantic import BaseModel
from typing import Optional
from models.textbook import TextbookNames


class InputBase(BaseModel):
    textbook_name: TextbookNames
    chapter_index: Optional[int] = 0
    section_index: Optional[int] = 0
    subsection_index: Optional[int] = 0


class ResultsBase(BaseModel):
    pass

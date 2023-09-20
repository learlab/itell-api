from pydantic import BaseModel
from typing import Optional
from models.textbook import TextbookNames


class InputBase(BaseModel):
    textbook_name: TextbookNames
    chapter_index: Optional[int] = 00
    section_index: Optional[int] = 00
    subsection_index: Optional[int] = 00


class ResultsBase(BaseModel):
    pass

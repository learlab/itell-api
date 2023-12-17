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

    # @root_validator
    # def chunk_slug_or_indexes(cls, values):
    #     if values.get("chunk_slug"):
    #         return values

    #     if (
    #         values.get("chapter_index") is None
    #         or values.get("subsection_index") is None
    #     ):
    #         raise ValueError(
    #             "AnswerInput requires either a chunk_slug if the content is on Strapi"
    #             " or a chapter_index and subsection_index if on SupaBase"
    #         )

    #     return values


class AnswerResults(BaseModel):
    score: float  # BLEURT or some other score
    is_passing: bool

from .textbook import TextbookNames
from .strapi import Chunk
from typing import Optional, Dict, Set, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from spacy.tokens import Doc


class SummaryInputStrapi(BaseModel):
    page_slug: str = Field(
        description="The slug of the current page.", example="the-first-chunk-99t"
    )
    summary: str
    focus_time: Dict[str, int] = Field(
        default=dict(),
        description="Keys are chunk slugs and values are focus times in seconds.",
        example={"introduction-to-law-79t": 20},
    )
    chat_history: Optional[str] = Field(
        default=None, description="The full chat history as a single string."
    )


class SummaryInputSupaBase(BaseModel):
    textbook_name: TextbookNames
    chapter_index: int
    section_index: Optional[int] = None
    summary: str
    focus_time: Dict[str, int] = Field(
        default=dict(),
        description="Keys are chunk slugs and values are focus times in seconds.",
        example={"introduction-to-law-79t": 20},
    )


class SummaryResults(BaseModel):
    containment: float
    containment_chat: Optional[float] = None
    similarity: float
    english: bool
    included_keyphrases: Set[str]
    suggested_keyphrases: Set[str]
    content: Optional[float] = None
    wording: Optional[float] = None


@dataclass
class Summary:
    """An intermediate object used for scoring summaries."""

    summary: Doc
    source: Doc
    chunks: list[Chunk]
    page_slug: str
    chat_history: Union[Doc, None]
    results: dict = field(default_factory=dict)

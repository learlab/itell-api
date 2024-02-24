from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class ChunkInput(BaseModel):
    text_slug: str
    module_slug: Optional[str] = None
    chapter_slug: Optional[str] = None
    page_slug: str
    chunk_slug: str
    content: str  # Chunk text content


class RetrievalStrategy(str, Enum):
    most_similar = "most_similar"
    least_similar = "least_similar"


class RetrievalInput(BaseModel, use_enum_values=True):
    text_slug: Optional[str] = None
    page_slug: str
    text: str  # text to compare to (student summary)
    similarity_threshold: Optional[float] = 0.0
    retrieve_strategy: Optional[RetrievalStrategy] = RetrievalStrategy.most_similar
    match_count: Optional[int] = 1


class Match(BaseModel):
    chunk: str
    content: str
    similarity: float


class RetrievalResults(BaseModel):
    matches: List[Match] = []

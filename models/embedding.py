from typing import Optional, List
from pydantic import BaseModel


class ChunkInput(BaseModel):
    text_slug: str
    module_slug: Optional[str] = None
    chapter_slug: Optional[str] = None
    page_slug: str
    chunk_slug: str
    content: str  # Chunk text content


class RetrievalInput(BaseModel):
    page_slug: str
    text: str  # text to compare to (student summary)
    similarity_threshold: Optional[float] = 0.3
    match_count: Optional[int] = 1


class Match(BaseModel):
    chunk_slug: str
    content: str
    similarity: float


class RetrievalResults(BaseModel):
    matches: List[Match]

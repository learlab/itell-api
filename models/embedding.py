from models.base import InputBase, ResultsBase
from typing import List
from pydantic import BaseModel

class ChunkInput(InputBase):
    text: str
    module: str
    chapter: str
    page: str
    chunk: str # Chunk slug
    content: str # Chunk text content

class RetrievalInput(InputBase):
    text: str
    page: str
    content: str # text to compare to (student summary)

class Match(BaseModel):
    chunk_slug: str
    content: str
    similarity: float

class RetrievalResults(ResultsBase):
    matches: List[Match]
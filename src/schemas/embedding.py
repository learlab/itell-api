from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


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
    page_slugs: list[str]
    text: str  # text to compare to (student summary)
    similarity_threshold: Optional[float] = 10.0 # Lower is more similar
    retrieve_strategy: Optional[RetrievalStrategy] = RetrievalStrategy.most_similar
    match_count: Optional[int] = 1


class Match(BaseModel):
    page: str
    chunk: str
    content: str
    similarity: float


class RetrievalResults(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "matches": [
                        {
                            "chunk": "test_chunk_1",
                            "content": "Lorem ipsum dolor sit amet...",
                            "similarity": 0.238420323227625,
                        }
                    ]
                }
            ]
        }
    )

    matches: List[Match] = []


class DeleteUnusedInput(BaseModel):
    page_slug: str
    chunk_slugs: list[str]

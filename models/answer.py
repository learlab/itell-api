from pydantic import root_validator
from models.base import InputBase, ResultsBase
from typing import Optional


class AnswerInput(InputBase):
    chunk_slug: Optional[str] = None
    answer: str

    @root_validator
    def chunk_slug_or_indexes(cls, values):
        if values.get("chunk_slug"):
            return values

        if (
            values.get("chapter_index") is None
            or values.get("subsection_index") is None
        ):
            raise ValueError(
                "AnswerInput requires either a chunk_slug if the content is on Strapi"
                " or a chapter_index and subsection_index if on SupaBase"
            )

        return values


class AnswerResults(ResultsBase):
    score: float  # BLEURT or some other score
    is_passing: bool

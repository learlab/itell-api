from typing import Optional
from models.base import InputBase, ResultsBase


class SummaryInput(InputBase):
    source: Optional[str] = None
    summary: str


class SummaryResults(ResultsBase):
    containment: float
    similarity: float
    included_keyphrases: set[str]
    suggested_keyphrases: set[str]
    content: Optional[float] = None
    wording: Optional[float] = None

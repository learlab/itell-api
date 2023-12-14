from typing import Optional, Dict, Set
from models.base import InputBase, ResultsBase


class SummaryInput(InputBase):
    summary: str
    focus_time: Dict[str, int] = dict()  # {"chunk_slug": "seconds", ...}


class SummaryResults(ResultsBase):
    containment: float
    similarity: float
    english: bool
    included_keyphrases: Set[str]
    suggested_keyphrases: Set[str]
    content: Optional[float] = None
    wording: Optional[float] = None

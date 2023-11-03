from typing import Optional, Dict, Set
from models.base import InputBase, ResultsBase


class TranscriptInput(InputBase):
    url: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None  # {"slug": "seconds", ...}


class TranscriptResults(ResultsBase):
    transcript: Optional[str] = None
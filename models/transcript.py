from typing import Optional, Dict, Set
from models.base import InputBase, ResultsBase


class TranscriptInput(InputBase):
    pass

class TranscriptResults(ResultsBase):
    transcript: Optional[str] = None
from typing import Optional, Dict, Set
from models.base import ResultsBase
from pydantic import BaseModel

class TranscriptInput(BaseModel):
    url: str = None
    start_time: int = None
    end_time: int = None

class TranscriptResults(ResultsBase):
    transcript: Optional[str] = None
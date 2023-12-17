from pydantic import BaseModel, AnyUrl
from typing import Optional


class TranscriptInput(BaseModel):
    url: AnyUrl  # Strapi validates that the URL is for YouTube
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class TranscriptResults(BaseModel):
    transcript: str

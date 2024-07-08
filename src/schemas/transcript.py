from typing import Optional

from pydantic import AnyUrl, BaseModel


class TranscriptInput(BaseModel):
    url: AnyUrl  # Strapi validates that the URL is for YouTube
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class TranscriptResults(BaseModel):
    transcript: str

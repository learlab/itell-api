from models.base import ResultsBase
from pydantic import BaseModel, Field

class TranscriptInput(BaseModel):
    url: str = Field(pattern=r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$')
    start_time: int = None
    end_time: int = None

class TranscriptResults(ResultsBase):
    transcript: str = None

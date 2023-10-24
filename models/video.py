from pydantic import BaseModel


class VideoInput(BaseModel):
    url: str


class VideoResult(BaseModel):
    text: str

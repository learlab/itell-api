from models.base import InputBase
from typing import Optional
from fastapi.responses import StreamingResponse


class ChatInput(InputBase):
    text_slug: str
    history: Optional[dict[str, str]]
    summary: Optional[str] = None
    message: str


ChatResult = StreamingResponse

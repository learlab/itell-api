from models.base import InputBase
from typing import Optional
from fastapi.responses import StreamingResponse


class ChatInput(InputBase):
    message: str
    history: Optional[dict]


ChatResult = StreamingResponse

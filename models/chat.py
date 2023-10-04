from models.base import InputBase, ResultsBase
from typing import Optional
from fastapi.responses import StreamingResponse


class ChatInput(InputBase):
    message: str
    history: Optional[dict]


ChatResult = StreamingResponse

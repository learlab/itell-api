from pydantic import BaseModel
from typing import Optional
from fastapi.responses import StreamingResponse


class ChatInput(BaseModel):
    """Strapi Only."""

    page_slug: str
    history: Optional[dict[str, str]]
    summary: Optional[str] = None
    message: str


ChatResult = StreamingResponse

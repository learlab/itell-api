from pydantic import BaseModel
from typing import Optional


class ChatInput(BaseModel):
    """Only works with texts that have their content stored in Strapi."""

    page_slug: str
    history: Optional[dict[str, str]]
    summary: Optional[str] = None
    message: str

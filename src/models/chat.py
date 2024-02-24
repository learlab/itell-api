from pydantic import BaseModel
from typing import Optional


class ChatInput(BaseModel):
    """Only works with texts that have their content stored in Strapi."""

    page_slug: str
    history: Optional[dict[str, str]] = None
    summary: Optional[str] = None
    message: str


class PromptInput(BaseModel):
    """Used for testing purposes. The user provides the full prompt that is
    sent to the model for generation."""

    message: str

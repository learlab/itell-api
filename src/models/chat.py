from pydantic import BaseModel, Field
from typing import Optional, Literal


class ChatMessage(BaseModel):
    agent: Literal["user", "bot"]
    text: str


class ChatInput(BaseModel):
    """Only works with texts that have their content stored in Strapi."""

    page_slug: str
    history: list[ChatMessage] = Field(
        default_factory=list,
        description=(
            "The full chat history as a list of {'agent': 'user'|'bot', 'text': str}"
            " dicts."
        ),
    )
    summary: Optional[str] = None
    message: str


class PromptInput(BaseModel):
    """Used for testing purposes. The user provides the full prompt that is
    sent to the model for generation."""

    message: str

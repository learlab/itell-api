from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    current_chunk: Optional[str] = None


class ChatInputSTAIRS(BaseModel):
    """Chat input for STAIRS dialogues."""

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
    current_chunk: str


class ChatInputCRI(BaseModel):
    """Explains why a student's response to a constructed response item is incorrect.
    Only works with texts that have their content stored in Strapi."""

    page_slug: str
    chunk_slug: str
    student_response: str


class PromptInput(BaseModel):
    """Used for testing purposes. The user provides the full prompt that is
    sent to the model for generation."""

    message: str


class ChatResponse(BaseModel):
    """Each response in the token stream will have this shape."""

    model_config = ConfigDict(extra="allow")  # Allow extra fields

    request_id: str
    text: str


class EventType(str, Enum):
    chat = "chat"
    summary_feedback = "summaryfeedback"  # First chunk when summary scoring
    content_feedback = "contentfeedback"
    language_feedback = "languagefeedback"
    constructed_response_feedback = "constructedresponsefeedback"
    think_aloud = "thinkaloud"

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChatMessage(BaseModel):
    agent: Literal["user", "bot"]
    text: str


class ChatInput(BaseModel):
    """Guide-on-the-side Chat Request."""

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


class ChatInputSERT(BaseModel):
    """SERT dialogue Chat Request.
    Returns a SERT question if history is empty or not provided.
    Otherwise, continues the conversation.
    """

    page_slug: str
    current_chunk: Optional[str] = None
    message: str
    history: list[ChatMessage] = Field(
        default_factory=list,
        description=(
            "The full chat history as a list of {'agent': 'user'|'bot', 'text': str}"
            " dicts."
        ),
    )
    summary: Optional[str] = None

    @model_validator(mode="after")
    def check_current_chunk_or_history(self):
        if self.history and not self.current_chunk:
            raise ValueError("current_chunk is required to continue a conversation.")
        return self


class ChatInputThinkAloud(BaseModel):
    """Think-aloud dialogue chat request.
    Returns a think-aloud if history is empty or not provided.
    Otherwise, continues the conversation.
    """

    page_slug: str
    chunk_slug: str
    message: Optional[str] = None
    history: list[ChatMessage] = Field(
        default_factory=list,
        description=(
            "The full chat history as a list of {'agent': 'user'|'bot', 'text': str}"
            " dicts."
        ),
    )
    question: str = Field(
        default=None, description="The CRI question that the student answered."
    )
    student_response: str = Field(
        default=None, description="The student's response to the CRI question."
    )


class ChatInputCRI(BaseModel):
    """Explains why a student's response to a constructed response item is incorrect."""

    page_slug: str
    chunk_slug: str
    student_response: str


class PromptInput(BaseModel):
    """Used for testing purposes. The provided message is sent directly to the model for generation."""

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
    constructed_response_feedback = "constructedresponsefeedback"
    think_aloud = "thinkaloud"

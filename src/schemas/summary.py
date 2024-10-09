from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from spacy.tokens import Doc

from .chat import ChatMessage
from .strapi import Chunk


class SummaryInputStrapi(BaseModel):
    page_slug: str = Field(
        description="The slug of the current page.", examples=["the-first-chunk-99t"]
    )
    summary: str
    focus_time: dict[str, int] = Field(
        default_factory=dict,
        description="Keys are chunk slugs and values are focus times in seconds.",
        examples=[{"introduction-to-law-79t": 20}],
    )
    chat_history: list[ChatMessage] = Field(
        default_factory=list,
        description=(
            "The full chat history as a list of {'agent': 'user'/'bot', 'text': str}"
            " dicts."
        ),
    )
    excluded_chunks: list[str] = Field(
        default_factory=list,
        description=(
            "The slugs of chunks that should be excluded from consideration for STAIRS."
            " For example, if the student has already correctly answered a constructed"
            " response item about a chunk."
        ),
    )
    score_history: list[float] = Field(
        default_factory=list,
        description="A list of the user's previous content scores.",
    )


class SummaryResults(BaseModel):
    containment: float
    containment_chat: Optional[float] = None
    similarity: float
    english: bool
    profanity: bool
    included_keyphrases: list[str]
    suggested_keyphrases: list[str]
    content: Optional[float] = None
    content_threshold: Optional[float] = None
    language: Optional[float] = None
    wording: Optional[float] = None  # Deprecated. Always None.


class ScoreType(str, Enum):
    containment = "Language Borrowing"
    containment_chat = "Language Borrowing (from iTELL AI)"
    similarity = "Relevance"
    english = "English"
    profanity = "Profanity"
    content = "Content"
    language = "Language"
    wording = "Wording"  # Deprecated.


class Feedback(BaseModel):
    is_passed: Optional[bool] = None
    prompt: Optional[str] = None


class AnalyticFeedback(BaseModel):
    type: ScoreType
    threshold: float | bool
    feedback: Feedback


class SummaryResultsWithFeedback(SummaryResults):
    is_passed: bool
    prompt: Optional[str] = None
    prompt_details: list[AnalyticFeedback]


class StreamingSummaryResults(SummaryResultsWithFeedback):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "containment": 0.0,
                    "containment_chat": None,
                    "similarity": 0.09705320000648499,
                    "english": True,
                    "profanity": False,
                    "included_keyphrases": [],
                    "suggested_keyphrases": [
                        "promote social justice",
                        "preserve individual rights",
                        "legislators",
                    ],
                    "content": None,
                    "language": None,
                    "is_passed": False,
                    "prompt": (
                        "Before moving onto the next page, you will need to revise the"
                        " summary you wrote using the feedback provided."
                    ),
                    "prompt_details": [
                        {
                            "type": "Language Borrowing",
                            "threshold": 0.6,
                            "feedback": {
                                "is_passed": False,
                                "prompt": (
                                    "You need to rely less on the language in the text"
                                    " and focus more on rewriting the key ideas."
                                ),
                            },
                        },
                        {
                            "type": "Language Borrowing (from iTELL AI)",
                            "threshold": 0.6,
                            "feedback": {"is_passed": False, "prompt": None},
                        },
                        {
                            "type": "Relevance",
                            "threshold": 0.5,
                            "feedback": {
                                "is_passed": False,
                                "prompt": (
                                    "To be successful, you need to stay on topic. Find"
                                    " the main ideas of the text and focus your summary"
                                    " on those ideas."
                                ),
                            },
                        },
                        {
                            "type": "Content",
                            "threshold": 0.07,
                            "feedback": {"is_passed": False, "prompt": None},
                        },
                        {
                            "type": "Language",
                            "threshold": 2.0,
                            "feedback": {"is_passed": False, "prompt": None},
                        },
                    ],
                },
                {
                    "request_id": "f77221b7cdd14fea879d48afbeaa5d61",
                    "text": "What do you think about the idea of",
                    "chunk": "Law-and-Politics-11t",
                    "question_type": "prediction",
                },
            ]
        }
    )
    request_id: str = Field(description="A unique identifier for the request.")
    text: str = Field(description="The token stream.")
    chunk: str = Field(description="The slug of the chunk selected for re-reading.")
    question_type: Literal[
        "paraphrasing", "elaboration", "logic", "prediction", "bridging"
    ]


class ChunkWithWeight(Chunk):
    # This is a Python object rather than json.
    KeyPhrase: Optional[list[str]] = None
    weight: float


@dataclass
class Summary:
    """An intermediate object used for scoring summaries."""

    summary: Doc
    source: Doc
    chunks: list[ChunkWithWeight]
    page_slug: str
    chat_history: Optional[list[ChatMessage]] = None
    bot_messages: Optional[Doc] = None
    excluded_chunks: list[str] = field(default_factory=lambda: [])

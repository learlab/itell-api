from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Optional, Union

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


class SummaryInputTest(SummaryInputStrapi):
    passing_content: bool = Field(
        description="Whether the summary response is passing or failing on content.",        
    )


class _SummaryResults(BaseModel):
    """Intermediate Object for Storing Summary Scores"""

    containment: float
    containment_chat: Optional[float] = None
    similarity: float
    english: bool
    profanity: bool
    included_keyphrases: list[str]
    suggested_keyphrases: list[str]
    content: Optional[float] = None
    content_threshold: Optional[float] = None


class ScoreType(str, Enum):
    containment = "Language Borrowing"
    containment_chat = "Language Borrowing (from iTELL AI)"
    similarity = "Relevance"
    english = "English"
    profanity = "Profanity"
    content = "Content"


class AnalyticFeedback(BaseModel):
    name: ScoreType
    is_passed: Optional[bool] = None
    score: Optional[Union[float, bool]] = None
    threshold: Optional[Union[float, bool]] = None
    feedback: Optional[str] = None


class SummaryMetrics(BaseModel):
    containment: AnalyticFeedback
    containment_chat: AnalyticFeedback
    content: AnalyticFeedback
    similarity: AnalyticFeedback
    english: AnalyticFeedback
    profanity: AnalyticFeedback


class SummaryResultsWithFeedback(BaseModel):
    is_passed: bool
    prompt: Optional[str] = None
    metrics: SummaryMetrics


class StreamingSummaryResults(SummaryResultsWithFeedback):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "is_passed": False,
                    "prompt": (
                        "Before moving onto the next page, you will need to revise the"
                        " summary you wrote using the feedback provided."
                    ),
                    "metrics": {
                        "containment": {
                            "name": "Language Borrowing",
                            "is_passed": True,
                            "score": 0.0,
                            "threshold": 0.6,
                            "feedback": "You need to rely less on the language in the text and focus more on rewriting the key ideas.",  # noqa: E501
                        },
                        "containment_chat": {
                            "name": "Language Borrowing (from iTELL AI)",
                            "is_passed": None,
                            "score": None,
                            "threshold": 0.6,
                            "feedback": "The summary is not too long or too short. It is just right.",  # noqa: E501
                        },
                        "similarity": {
                            "name": "Relevance",
                            "is_passed": False,
                            "score": 0.09705320000648499,
                            "threshold": 0.5,
                            "feedback": "To be successful, you need to stay on topic. Find the main ideas of the text and focus your summary on those ideas.",  # noqa: E501
                        },
                        "english": {
                            "name": "English",
                            "is_passed": True,
                            "score": True,
                            "threshold": False,
                            "feedback": None,
                        },
                        "profanity": {
                            "name": "Profanity",
                            "is_passed": True,
                            "score": True,
                            "threshold": False,
                            "feedback": None,
                        },
                    },
                    "included_keyphrases": [],
                    "suggested_keyphrases": [
                        "promote social justice",
                        "preserve individual rights",
                        "legislators",
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

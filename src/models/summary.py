from .textbook import TextbookNames
from .strapi import Chunk
from typing import Optional, Dict, Union
from pydantic import BaseModel, Field
from dataclasses import dataclass
from spacy.tokens import Doc
from enum import Enum
from typing import Literal


class SummaryInputStrapi(BaseModel):
    page_slug: str = Field(
        description="The slug of the current page.", example="the-first-chunk-99t"
    )
    summary: str
    focus_time: Dict[str, int] = Field(
        default=dict(),
        description="Keys are chunk slugs and values are focus times in seconds.",
        example={"introduction-to-law-79t": 20},
    )
    chat_history: Optional[str] = Field(
        default=None, description="The full chat history as a single string."
    )


class SummaryInputSupaBase(BaseModel):
    textbook_name: TextbookNames = Field(deprecated=True, description="Use page_slug.")
    chapter_index: int = Field(deprecated=True, description="Use page_slug.")
    section_index: Optional[int] = Field(
        None, deprecated=True, description="Use page_slug."
    )
    summary: str
    focus_time: Dict[str, int] = Field(
        default=dict(),
        description="Keys are chunk slugs and values are focus times in seconds.",
        example={"introduction-to-law-79t": 20},
    )


class SummaryResults(BaseModel):
    originality: float
    originality_chat: Optional[float] = None
    relevance: float
    english: bool
    included_keyphrases: list[str]
    suggested_keyphrases: list[str]
    content: Optional[float] = None
    wording: Optional[float] = None


class ScoreType(str, Enum):
    originality = "Language Borrowing"
    originality_chat = "Language Borrowing (from iTELL AI)"
    relevance = "Topic Similarity"
    english = "English"
    content = "Content"
    wording = "Wording"


class Feedback(BaseModel):
    is_passed: Optional[bool] = None
    prompt: Optional[str] = None


class AnalyticFeedback(BaseModel):
    type: ScoreType
    feedback: Feedback


class SummaryResultsWithFeedback(SummaryResults):
    is_passed: bool
    prompt: Optional[str] = None
    prompt_details: list[AnalyticFeedback]


class StreamingSummaryResults(SummaryResultsWithFeedback):
    request_id: str = Field(description="A unique identifier for the request.")
    text: str = Field(description="The token stream.")
    chunk: str = Field(description="The slug of the chunk selected for re-reading.")
    question_type: Literal[
        "paraphrasing", "elaboration", "logic", "prediction", "bridging"
    ]

    class Config:
        schema_extra = {
            "examples": [
                {
                    "originality": 0.0,
                    "originality_chat": None,
                    "relevance": 0.09705320000648499,
                    "english": True,
                    "included_keyphrases": [],
                    "suggested_keyphrases": [
                        "promote social justice",
                        "preserve individual rights",
                        "legislators",
                    ],
                    "content": None,
                    "wording": None,
                    "is_passed": False,
                    "prompt": (
                        "Before moving onto the next page, you will need to revise the"
                        " summary you wrote using the feedback provided."
                    ),
                    "prompt_details": [
                        {
                            "type": "Language Borrowing",
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
                            "feedback": {"is_passed": False, "prompt": None},
                        },
                        {
                            "type": "Topic Relevance",
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
                            "feedback": {"is_passed": False, "prompt": None},
                        },
                        {
                            "type": "Wording",
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


class ChunkWithWeight(Chunk):
    KeyPhrase: Optional[list[str]]  # This is a Python object rather than json.
    weight: float


@dataclass
class Summary:
    """An intermediate object used for scoring summaries."""

    summary: Doc
    source: Doc
    chunks: list[ChunkWithWeight]
    page_slug: str
    chat_history: Union[Doc, None]

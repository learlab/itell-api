"""
Pydantic schemas for Strapi v5 API responses. Expected response structures:

PageWithVolumeResponse
├── data: List[PageWithVolume]
│   └── PageWithVolume
│       ├── id: int
│       ├── documentId: str
│       ├── Title: str
│       ├── Slug: str
│       ├── HasSummary: bool
│       ├── ReferenceSummary: Optional[str]
│       ├── createdAt: datetime
│       ├── updatedAt: datetime
│       ├── publishedAt: datetime
│       └── Volume
│           ├── id: int
│           ├── documentId: str
│           ├── Title: str
│           ├── Owner: str
│           ├── Description: Optional[str]
│           ├── Slug: str
│           ├── createdAt: datetime
│           ├── updatedAt: datetime
│           └── publishedAt: datetime
└── meta
    └── pagination
        ├── page: int
        ├── pageSize: int
        ├── pageCount: int
        └── total: int

PageWithChunksResponse
├── data: List[PageWithContent]
│   └── PageWithContent
│       ├── id: int
│       ├── documentId: str
│       ├── Title: str
│       ├── Slug: str
│       ├── HasSummary: bool
│       ├── ReferenceSummary: Optional[str]
│       ├── createdAt: datetime
│       ├── updatedAt: datetime
│       ├── publishedAt: datetime
│       └── Content: List[Chunk]
│           └── Chunk
│               ├── __component: str
│               ├── Slug: str
│               ├── Header: str
│               ├── CleanText: str
│               ├── KeyPhrase: Optional[str]
│               ├── QuestionAnswerResponse: Optional[str]
│               ├── Question: Optional[str]
│               └── ConstructedResponse: Optional[str]
└── meta (ignored)
    └── pagination
        ├── page: int
        ├── pageSize: int
        ├── pageCount: int
        └── total: int
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Chunk(BaseModel):
    component_type: str = Field(..., alias="__component")
    slug: str = Field(..., alias="Slug")
    header: str = Field(..., alias="Header")
    clean_text: str = Field(..., alias="CleanText")
    keyphrases: Optional[str | list[str]] = Field(None, alias="KeyPhrase")
    question_answer_response: Optional[str] = Field(
        None, alias="QuestionAnswerResponse"
    )
    question: Optional[str] = Field(None, alias="Question")
    constructed_response: Optional[str] = Field(None, alias="ConstructedResponse")

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    @field_validator("keyphrases", mode="before")
    @classmethod
    def split_key_phrases(cls, v: Optional[str | list[str]]) -> Optional[list[str]]:
        if not v:
            return None
        elif isinstance(v, list):
            return v
        else:
            return [phrase.strip() for phrase in v.split(",")]


class BaseStrapiModel(BaseModel):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    published_at: datetime = Field(..., alias="publishedAt")

    model_config = {"populate_by_name": True}


class Volume(BaseStrapiModel):
    slug: str = Field(..., alias="Slug")
    title: str = Field(..., alias="Title")
    owner: str = Field(..., alias="Owner")
    description: Optional[str] = Field(None, alias="Description")


class Page(BaseStrapiModel):
    slug: str = Field(..., alias="Slug")
    title: str = Field(..., alias="Title")
    has_summary: bool = Field(..., alias="HasSummary")
    reference_summary: Optional[str] = Field(None, alias="ReferenceSummary")


class PageWithContent(Page):
    content: list[Chunk] = Field(..., alias="Content")

    @field_validator("content")
    @classmethod
    def validate_data(cls, v: list[Chunk]) -> list[Chunk]:
        if not v:
            raise ValueError("Strapi did not return any chunks for this page.")
        return v


class PageWithVolume(Page):
    volume: Volume = Field(..., alias="Volume")

    @field_validator("volume")
    @classmethod
    def validate_data(cls, v: Volume) -> Volume:
        if not v:
            raise ValueError(
                "Strapi did not return a volume associated with this page."
            )
        return v


class PageWithVolumeResponse(BaseModel):
    data: list[PageWithVolume]

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: list[PageWithVolume]) -> list[PageWithVolume]:
        if not v:
            raise ValueError("Strapi did not return a page.")
        return v

    model_config = {"populate_by_name": True}


class PageWithChunksResponse(BaseModel):
    data: list[PageWithContent] = Field(..., min_length=1)

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: list[PageWithContent]) -> list[PageWithContent]:
        if not v:
            raise ValueError("Strapi did not return a page.")
        return v

    model_config = {"populate_by_name": True}

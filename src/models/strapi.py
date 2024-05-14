from typing import Optional
from pydantic import BaseModel, Field, Json, field_validator

from typing import TypeVar, Generic


class Chunk(BaseModel):
    component_type: str = Field(..., alias="__component")
    Slug: str
    id: int
    Header: str
    CleanText: str
    KeyPhrase: Optional[Json[list[str]]] = None
    QuestionAnswerResponse: Optional[Optional[str]] = None
    Question: Optional[str] = None
    ConstructedResponse: Optional[str] = None


class Page(BaseModel):
    slug: str
    Title: str
    HasSummary: bool


class Text(BaseModel):
    slug: str
    Title: str
    Owner: str
    Description: Optional[str] = None


# Page Types


class Content(Page):
    Content: list[Chunk]

    @field_validator("Content")
    def page_must_have_text(cls, v):
        if len(v) == 0:
            raise ValueError("Strapi returned 0 chunks for this page.")

        return v


# Fancy Generic Types for Defining Pages Populated with Specific Values

Populus = TypeVar("Populus")


class Response(BaseModel, Generic[Populus]):
    data: Populus


class PopulatedItem(BaseModel, Generic[Populus]):
    id: int
    attributes: Populus


# Constructed Types
class _PageWithText(Page):
    text: Response[PopulatedItem[Text]]


class PageWithText(BaseModel):
    data: list[PopulatedItem[_PageWithText]]

    @field_validator("data")
    def page_must_have_text(cls, v):
        if len(v) == 0:
            raise ValueError("Empty response from Strapi.")

        return v


class PageWithChunks(BaseModel):
    data: list[PopulatedItem[Content]]

    @field_validator("data")
    def page_must_have_chunks(cls, v):
        if len(v) == 0:
            raise ValueError("Empty response from Strapi.")

        return v

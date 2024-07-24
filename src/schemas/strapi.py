from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, Json, field_validator


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
    Slug: str
    Title: str
    HasSummary: bool


class Volume(BaseModel):
    Slug: str
    Title: str
    Owner: str
    Description: Optional[str] = None


# Page Types
class Content(Page):
    Content: list[Chunk]

    @field_validator("Content")
    def page_must_have_chunks(cls, v):
        if len(v) == 0:
            raise ValueError("Strapi returned 0 chunks for this page.")

        return v


"""
This is a bit more complex. We want to validate the following response structures:

PageWithVolume
├── data: List[PopulatedItem[ItemWithVolume]]
│   ├── PopulatedItem
│   │   ├── id: int
│   │   └── attributes: ItemWithVolume
│   │       └── Volume: Response[PopulatedItem[Volume]]
│   │           ├── data: PopulatedItem[Volume]
│   │           │   ├── id: int
│   │           │   └── attributes: Volume

PageWithChunks
├── data: List[PopulatedItem[Content]]
│   ├── PopulatedItem
│   │   ├── id: int
│   │   └── attributes: Content
"""

Populus = TypeVar("Populus")


class Response(BaseModel, Generic[Populus]):
    data: Populus


class PopulatedItem(BaseModel, Generic[Populus]):
    id: int
    attributes: Populus


# Constructed Types
class ItemWithVolume(Page):
    Volume: Response[PopulatedItem[Volume]]


class PageWithVolume(BaseModel):
    data: list[PopulatedItem[ItemWithVolume]]

    @field_validator("data")
    @classmethod
    def page_must_have_text(cls, v):
        if len(v) == 0:
            raise ValueError("Empty response from Strapi.")

        return v


class PageWithChunks(BaseModel):
    data: list[PopulatedItem[Content]]

    @field_validator("data")
    @classmethod
    def page_must_have_chunks(cls, v):
        if len(v) == 0:
            raise ValueError("Empty response from Strapi.")

        return v

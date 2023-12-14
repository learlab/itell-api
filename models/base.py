from pydantic import BaseModel, Field, root_validator
from typing import Optional
from models.textbook import TextbookNames


class InputBase(BaseModel):
    page_slug: Optional[str] = None
    textbook_name: Optional[TextbookNames] = Field(
        description="This field is deprecated and should only be used for legacy textbooks that are not in Strapi.",
    )
    chapter_index: Optional[int] = Field(
        0,
        description="This field is deprecated and should only be used for legacy textbooks that are not in Strapi.",
    )
    section_index: Optional[int] = Field(
        0,
        description="This field is deprecated and should only be used for legacy textbooks that are not in Strapi.",
    )
    subsection_index: Optional[int] = Field(
        0,
        description="This field is deprecated and should only be used for legacy textbooks that are not in Strapi.",
    )

    @root_validator
    def textbook_name_or_page_slug(cls, values):
        if values.get("textbook_name") is None and values.get("page_slug") is None:
            raise ValueError(
                "Specify either textbook_name if the content is on SupaBase or page_slug if the conent is on Strapi."
            )
        return values


class ResultsBase(BaseModel):
    pass

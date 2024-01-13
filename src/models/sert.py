from pydantic import BaseModel


class SertInput(BaseModel):
    """STAIRS uses the same chat model as our guide on the side,
    but requires the summary field and no user message."""

    page_slug: str
    summary: str

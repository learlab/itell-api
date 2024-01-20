from pydantic import BaseModel, Field
from typing import Dict


class SertInput(BaseModel):
    """STAIRS uses the same chat model as our guide on the side,
    but requires the summary field and no user message."""

    page_slug: str
    summary: str
    stream: bool = Field(default=True, description="Whether to stream the response.")
    focus_time: Dict[str, int] = Field(
        default=dict(),
        description="Keys are chunk slugs and values are focus times in seconds.",
        example={"introduction-to-law-79t": 20},
    )

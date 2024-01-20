from pydantic import BaseModel
from typing import Dict


class SertInput(BaseModel):
    """STAIRS uses the same chat model as our guide on the side,
    but requires the summary field and no user message."""

    page_slug: str
    summary: str
    stream: bool = True
    focus_time: Dict[str, int] = dict()  # {"chunk_slug": "seconds", ...}

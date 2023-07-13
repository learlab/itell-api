from pydantic import BaseModel
from typing import Optional

textbook_names = [
    'macroeconomics-2e',
    'think-python-2e',
]

class SummaryInput(BaseModel):
    textbook_name: str # macroeconomics-2e, think-python-2e
    chapter_index: int | None = None
    section_index: int | None = None
    source: Optional[str]
    summary: str

    @field_validator('textbook_name')
    def validate_textbook_name(cls, v):
        if v not in textbook_names:
            raise ValueError(f'Invalid textbook name: {v}')
        return v

class SummaryResults(BaseModel):
    containment: float
    similarity: float
    profanity: bool
    included_keyphrases: set[str]
    suggested_keyphrases: set[str]
    content: float | None = None
    wording: float | None = None

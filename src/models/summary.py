from pydantic import BaseModel


class SummaryInput(BaseModel):
    text: str

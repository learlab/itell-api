from pydantic import BaseModel, ConfigDict


class AnswerInputStrapi(BaseModel):
    page_slug: str
    chunk_slug: str
    answer: str


class AnswerResults(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"score": 0.0, "is_passing": False}]}
    )
    score: float  # BLEURT or some other score
    is_passing: bool

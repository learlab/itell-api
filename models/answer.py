from models.base import InputBase, ResultsBase


class AnswerInput(InputBase):
    chunk_slug: str
    answer: str


class AnswerResults(ResultsBase):
    score: float  # BLEURT or some other score
    is_passing: bool

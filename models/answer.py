from models.base import InputBase, ResultsBase


class AnswerInput(InputBase):
    answer: str


class AnswerResults(ResultsBase):
    score: float  # BLEURT or some other score
    is_passing: bool

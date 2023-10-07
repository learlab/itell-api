from models.base import InputBase, ResultsBase


class AnswerInput(InputBase):
    answer: str


class AnswerResults(ResultsBase):
    score: float  # in [0,1,2] 0 means incorrect, 2 means correct, 1 means model disagreement
    is_passing: bool
    results: dict # dictionary contining BLEURT score and MPnet label
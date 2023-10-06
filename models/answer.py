from models.base import InputBase, ResultsBase


class AnswerInput(InputBase):
    answer: str


class AnswerResults(ResultsBase):
    score: float  # in [0, 1, 2]. 0 means wrong, 2 means correct, 1 means models disagree
    logits: dict 
    is_passing: bool

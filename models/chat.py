from models.base import InputBase, ResultsBase


class ChatInput(InputBase):
    message: str


class ChatResult(ResultsBase):
    message: str

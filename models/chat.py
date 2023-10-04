from models.base import InputBase, ResultsBase
from typing import Optional

class ChatInput(InputBase):
    message: str
    history: Optional[dict]


class ChatResult(ResultsBase):
    message: str

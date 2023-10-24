from models.base import InputBase, ResultsBase
from typing import List


class ChunkInput(InputBase):
    text: str


class ChunkEmbedding(ResultsBase):
    embed: List[float]

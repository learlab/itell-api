from models.base import InputBase, ResultsBase


class ChunkInput(InputBase):
    text: str


class ChunkEmbedding(ResultsBase):
    embed: list[float]

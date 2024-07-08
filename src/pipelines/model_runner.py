from typing import Generator, Iterable

import ray
import spacy
from spacy.tokens import Doc

from .answer import AnswerPipeline
from .embed import EmbeddingPipeline
from .summary import LongformerPipeline, SummaryPipeline


@ray.remote
class Pipes:
    def __init__(self):
        self.embedding_pipe = EmbeddingPipeline()
        self.spacy = spacy.load("en_core_web_sm", enable=["tagger", "lemmatizer"])
        self.answer_pipe = AnswerPipeline()
        self.content_pipe = LongformerPipeline("tiedaar/longformer-content-global")
        self.language_pipe = SummaryPipeline("tiedaar/language-beyond-the-source")

    def embed(self, text: str) -> list[float]:
        return self.embedding_pipe(text)

    def nlp(self, text: str) -> Doc:
        return self.spacy(text)

    # def nlp_pipe(self, texts: Iterable[str]) -> Iterable[Doc]:
    #     for doc in self.spacy.pipe(texts):
    #         yield doc

    def answer(self, candidate: str, reference: str) -> int:
        return self.answer_pipe(candidate, reference)

    def content(self, text: str) -> float:
        return self.content_pipe.score(text)

    def language(self, text: str) -> float:
        return self.language_pipe.score(text)

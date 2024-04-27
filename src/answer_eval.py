from .models.answer import AnswerInputStrapi, AnswerResults
from .pipelines.answer import AnswerPipeline
from .connections.strapi import Strapi
from fastapi import HTTPException
from transformers import logging

logging.set_verbosity_error()

strapi = Strapi()
answer_pipe = AnswerPipeline()


class Answer:
    def __init__(self, gold_answer: str, answer: str) -> None:
        self.gold = gold_answer
        self.answer = answer
        self.results = {}

    def score_answer(self) -> None:
        """
        Returns passing score ONLY if both BLEURT and MPnet agree that it is passing
        """
        res = answer_pipe(self.answer, self.gold)

        self.results["score"] = res
        if res < 2:
            self.results["is_passing"] = False
        else:
            self.results["is_passing"] = True


async def answer_score(answer_input: AnswerInputStrapi) -> AnswerResults:
    chunk = await strapi.get_chunk(answer_input.page_slug, answer_input.chunk_slug)

    if chunk.ConstructedResponse is None:
        raise HTTPException(
            status_code=404,
            detail="Requested Chunk does not have a ConstructedResponse",
        )

    answer = Answer(chunk.ConstructedResponse, answer_input.answer)
    answer.score_answer()

    return AnswerResults(**answer.results)

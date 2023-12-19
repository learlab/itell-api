from .models.answer import AnswerInputStrapi, AnswerResults
from .pipelines.answer import AnswerPipeline
from .connections.strapi import Strapi

from transformers import logging

logging.set_verbosity_error()

strapi = Strapi()
answer_pipe = AnswerPipeline()


class Answer:
    def __init__(self, content: list[dict[str, str]], answer: str) -> None:
        self.question = content[0]["ConstructedResponse"]
        self.answer = answer
        self.results = {}

    def score_answer(self) -> None:
        """
        Returns passing score ONLY if both BLEURT and MPnet agree that it is passing
        """
        res = answer_pipe(self.answer, self.question)

        self.results["score"] = res
        if res < 2:
            self.results["is_passing"] = False
        else:
            self.results["is_passing"] = True


async def answer_score(answer_input: AnswerInputStrapi) -> AnswerResults:
    response = await strapi.get_entries(
        plural_api_id="pages",
        filters={"slug": {"$eq": answer_input.page_slug}},
        populate={"Content": {"filters": {"Slug": {"$eq": answer_input.chunk_slug}}}},
    )

    content = response["data"][0]["attributes"]["Content"]

    answer = Answer(content, answer_input.answer)
    answer.score_answer()

    return AnswerResults(**answer.results)

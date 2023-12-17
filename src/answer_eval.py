from .models.answer import AnswerInputStrapi, AnswerResults
from .pipelines.answer import AnswerPipeline
from .connections.strapi import Strapi
from transformers import logging
from fastapi import HTTPException

logging.set_verbosity_error()

answer_pipe = AnswerPipeline()


class Answer:
    db: Strapi = Strapi()

    async def __init__(self, answer_input: AnswerInputStrapi):
        response = self.db.fetch(
            f"/api/pages?filters[slug][$eq]={answer_input.page_slug}"
            f"&populate[Content][filters][Slug][$eq]={answer_input.chunk_slug}"
        )

        self.content = await response["data"][0]["attributes"]["Content"]

        if len(self.content) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No Content found for {answer_input.chunk_slug} in {answer_input.page_slug}.",
            )
        if not self.content[0]["ConstructedResponse"]:
            raise HTTPException(
                status_code=404,
                detail=f"No ConstructedResponse found for {answer_input.chunk_slug}",
            )
        self.question = self.content[0]["ConstructedResponse"]
        self.answer = answer_input.answer
        self.results = {}

    def score_answer(self) -> None:
        """
        This currently returns passing score ONLY if both BLEURT and MPnet agree that it is passing
        """
        res = answer_pipe(self.answer, self.question)

        self.results["score"] = res
        if res < 2:
            self.results["is_passing"] = False
        else:
            self.results["is_passing"] = True


async def answer_score(answer_input: AnswerInputStrapi) -> AnswerResults:
    answer = Answer(answer_input)
    answer.score_answer()

    return AnswerResults(**answer.results)

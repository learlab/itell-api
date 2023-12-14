from models.answer import AnswerInput, AnswerResults
from transformers import logging
from pipelines.answer import AnswerPipeline
from connections.strapi import Strapi

logging.set_verbosity_error()

answer_pipe = AnswerPipeline()


class Answer:
    db: Strapi = Strapi()

    def __init__(self, answer_input: AnswerInput):
        response = self.db.fetch(
            f"/api/pages?populate[Content][filters][slug][$eq]={AnswerInput.chunk_slug}"
        )

        self.content = response["data"][0]["attributes"]["Content"]

        self.answer = answer_input.answer
        self.results = {}

    def score_answer(self) -> None:
        """
        This currently returns passing score ONLY if both BLEURT and MPnet agree that it is passing
        """

        correct_answer = self.content["ConstructedResponse"]
        res = answer_pipe(self.answer, correct_answer)

        self.results["score"] = res
        if res < 2:
            self.results["is_passing"] = False
        else:
            self.results["is_passing"] = True


async def answer_score(answer_input: AnswerInput) -> AnswerResults:
    answer = Answer(answer_input)
    answer.score_answer()

    return AnswerResults(**answer.results)

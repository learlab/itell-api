from fastapi import HTTPException
from transformers import logging

from ..dependencies.strapi import Strapi
from ..pipelines.model_runner import Pipes
from ..schemas.answer import AnswerInputStrapi, AnswerResults

logging.set_verbosity_error()


async def answer_score(
    answer_input: AnswerInputStrapi, strapi: Strapi, pipes: Pipes
) -> AnswerResults:
    chunk = await strapi.get_chunk(answer_input.page_slug, answer_input.chunk_slug)

    if chunk.ConstructedResponse is None:
        raise HTTPException(
            status_code=404,
            detail="Requested Chunk does not have a ConstructedResponse",
        )

    results = {}
    results["score"] = await pipes.answer.remote(
        chunk.ConstructedResponse, answer_input.answer
    )

    results["is_passing"] = False if results["score"] < 2 else True

    return AnswerResults(**results)

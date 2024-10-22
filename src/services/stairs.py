"""SERT: Self-Explanation and Reading Strategy Training."""

import random
from typing import AsyncGenerator

from fastapi import HTTPException
from jinja2 import Template
from vllm.sampling_params import SamplingParams

from src.dependencies.faiss import FAISS_Wrapper

from ..dependencies.strapi import Strapi
from ..pipelines.chat import chat_pipeline
from ..schemas.chat import ChatInputCRI, EventType
from ..schemas.embedding import RetrievalInput, RetrievalStrategy
from ..schemas.strapi import Volume
from ..schemas.summary import ChunkWithWeight, Summary

with open("templates/sert_question.jinja2", "r", encoding="utf8") as file_:
    sert_question_template = Template(file_.read())

with open("templates/think_aloud.jinja2", "r", encoding="utf8") as file_:
    think_aloud_template = Template(file_.read())


def weight_chunks_with_similarity(reading_time_score, similarity):
    return reading_time_score * similarity


question_type_definitions = {
    "paraphrasing": "A paraphrasing question asks readers to restate the text in different words.",  # noqa E501
    "elaboration": "An elaboration question asks readers to make inferences that link what is in the text or sentence to the reader’s background knowledge.",  # noqa E501
    "logic": "A logic question asks readers to use general knowledge or logic to infer meaning. It encourages readers to use logic and common sense to help them make sense of the text.",  # noqa E501
    "prediction": "A prediction question asks readers to think about what might come next in the text. It encouranges readers to predict next ideas or steps.",  # noqa E501
    "bridging": "A bridging question asks readers to link ideas and understand the relations between text segments. It will encourage readers to generate bridging inferences across sentences and to build a coherent mental model.",  # noqa E501
}


async def select_chunk(
    summary: Summary,
    text_meta: Volume,
    faiss: FAISS_Wrapper,
) -> ChunkWithWeight:
    """Select a chunk for rereading based on the user's summary and reading behavior."""

    # Retrieve the chunks that are the least similar to the student's summary.
    least_similar_chunks = await faiss.retrieve_chunks(
        RetrievalInput(
            text_slug=text_meta.Slug,
            page_slugs=[summary.page_slug],
            text=summary.summary.text,
            retrieve_strategy=RetrievalStrategy.least_similar,
            match_count=10,
        )
    )

    if len(least_similar_chunks.matches) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found for '{summary.page_slug}' in the vector store.",
        )

    # Make a dictionary to look up similarity scores by Slug
    similarity_dict = {
        match.chunk: match.similarity for match in least_similar_chunks.matches
    }

    for chunk in similarity_dict.keys():
        if chunk in summary.excluded_chunks:
            # +1 to similarity of excluded chunks will make them unlikely selections
            # May still be selected if no other chunks are available
            similarity_dict[chunk] += 1

    # Calculate final score for rereading: reading_time_score * similarity
    chunks: list[tuple[ChunkWithWeight, float]] = [
        (chunk, (chunk.weight * similarity_dict[chunk.Slug]))
        for chunk in summary.chunks
        if chunk.Slug in similarity_dict
    ]

    if len(chunks) == 0:
        raise HTTPException(
            status_code=404,
            detail="No chunks in the vector store match the provided list of chunks.",
        )

    # Select the chunk with the lowest score
    selected_chunk, _ = min(chunks, key=lambda x: x[1])

    return selected_chunk


async def sert_question(
    summary: Summary, strapi: Strapi, faiss: FAISS_Wrapper
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(summary.page_slug)

    selected_chunk = await select_chunk(summary, text_meta, faiss)

    chunk_text = selected_chunk.CleanText[
        : min(2000, len(selected_chunk.CleanText))  # first 2,000 characters
    ]

    question_type = random.choice(list(question_type_definitions.keys()))

    # Construct the SERT prompt
    prompt = sert_question_template.render(
        text_name=text_meta.Title,
        excerpt_chunk=chunk_text,
        student_summary=summary.summary.text,
        question_type=question_type,
        question_type_definition=question_type_definitions[question_type],
    )

    sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)

    return await chat_pipeline(
        prompt,
        sampling_params,
        event_type=EventType.content_feedback,
        chunk=selected_chunk.Slug,
        question_type=question_type,
    )


async def think_aloud(
    input_body: ChatInputCRI, strapi: Strapi, faiss: FAISS_Wrapper
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(input_body.page_slug)
    chunk = await strapi.get_chunk(input_body.page_slug, input_body.chunk_slug)

    # Construct the STAIRS prompt
    prompt = think_aloud_template.render(
        text_name=text_meta.Title,
        text_info=text_meta.Description,
        context=chunk.CleanText,
    )

    sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)

    return await chat_pipeline(
        prompt,
        sampling_params,
        event_type=EventType.think_aloud,
        chunk=input_body.chunk_slug,
    )

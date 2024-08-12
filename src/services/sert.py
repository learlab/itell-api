"""SERT: Self-Explanation and Reading Strategy Training."""

import random
from typing import AsyncGenerator

from fastapi import HTTPException
from jinja2 import Template
from vllm.sampling_params import SamplingParams

from ..dependencies.faiss import FAISS
from ..dependencies.strapi import Strapi
from ..dependencies.supabase import SupabaseClient
from ..pipelines.chat import chat_pipeline
from ..schemas.chat import EventType
from ..schemas.embedding import RetrievalInput, RetrievalStrategy
from ..schemas.summary import ChunkWithWeight, Summary

with open("templates/sert.jinja2", "r", encoding="utf8") as file_:
    prompt_template = Template(file_.read())

question_type_definitions = {
    "paraphrasing": "A paraphrasing question asks readers to restate the text in different words.",  # noqa E501
    "elaboration": "An elaboration question asks readers to make inferences that link what is in the text or sentence to the reader’s background knowledge.",  # noqa E501
    "logic": "A logic question asks readers to use general knowledge or logic to infer meaning. It encourages readers to use logic and common sense to help them make sense of the text.",  # noqa E501
    "prediction": "A prediction question asks readers to think about what might come next in the text. It encouranges readers to predict next ideas or steps.",  # noqa E501
    "bridging": "A bridging question asks readers to link ideas and understand the relations between text segments. It will encourage readers to generate bridging inferences across sentences and to build a coherent mental model.",  # noqa E501
}


def weight_chunks_with_similarity(reading_time_score, similarity):
    return reading_time_score * similarity


async def sert_chat(
    summary: Summary, strapi: Strapi, faiss: FAISS
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(summary.page_slug)

    # Retrieve the chunks that are the least similar to the student's summary
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

    # print(similarity_dict)

    for chunk in similarity_dict.keys():
        if chunk in summary.excluded_chunks:
            # -1 to similarity of excluded chunks will make them unlikely selections
            # May still be selected if no other chunks are available
            similarity_dict[chunk] -= 1

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

    # Select the chunk with the highest score
    selected_chunk, _ = max(chunks, key=lambda x: x[1])

    chunk_text = selected_chunk.CleanText[
        : min(2000, len(selected_chunk.CleanText))  # first 2,000 characters
    ]

    question_type = random.choice(list(question_type_definitions.keys()))

    # Construct the SERT prompt
    prompt = prompt_template.render(
        text_name=text_meta.Title,
        context=chunk_text,
        student_summary=summary.summary.text,
        question_type=question_type,
        question_type_definition=question_type_definitions[question_type],
    )
    print(prompt)

    sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)

    return await chat_pipeline(
        prompt,
        sampling_params,
        event_type=EventType.content_feedback,
        chunk=selected_chunk.Slug,
        question_type=question_type,
    )

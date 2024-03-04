"""SERT: Self-Explanation and Reading Strategy Training."""
# flake8: noqa E501
from .models.summary import Summary, ChunkWithWeight
from .models.embedding import RetrievalInput, RetrievalStrategy
from .embedding import chunks_retrieve
from .pipelines.chat import chat_pipeline
from .connections.strapi import Strapi
from typing import AsyncGenerator

import random
from vllm.sampling_params import SamplingParams
from fastapi import HTTPException

strapi = Strapi()

question_type_definitions = {
    "paraphrasing": (
        "restating the text in different words. Preferably, in the reader’s own words."
        " It is an important part of the explanation process because readers often"
        " paraphrase the sentence in order to begin an explanation. Paraphrases are"
        " important because they help the reader to better understand the information"
        " in the sentences, and thus help the reader, particularly less skilled"
        " readers, to develop a better understanding of the text. Essentially, the act"
        " of paraphrasing externalizes the reader’s understanding. This process can"
        " force the reader to fill in conceptual gaps and facilitates the activation of"
        " relevant concepts that are necessary to generate inferences."
    ),
    "elaboration": (
        "the process of making inferences that link what is in the text or sentence to"
        " related to a reader’s background knowledge. Readers use specific prior"
        " knowledge or learned experiences to understand a text by developing"
        " inferences based on specific background knowledge."
    ),
    "logic": (
        "using general knowledge or logic to infer meaning. Does not depend on"
        " background knowledge unique to a reader but rather general knowledge of the"
        " world. Helps low-knowledge readers make sense of unfamiliar text. Encourages"
        " students to use logic and common sense helps them to understand that it is"
        " possible to make sense of the text, and go beyond the text, without knowing a"
        " lot about the topic."
    ),
    "prediction": (
        "thinking about what might be coming next in the text. Asking readers to"
        " predict next ideas or steps in a text that enhance thinking about the text"
        " from a global and not a local perspective."
    ),
    "bridging": (
        "the process of linking ideas and understanding the relations between"
        " separate text segments. Readers merge individual ideas from the text into"
        " coherent text representation. Making bridging inferences is critical to text"
        " comprehension because texts normally do not (or cannot) state all of the"
        " relevant information. Therefore, to successfully comprehend a text, the"
        " reader must generate bridging inferences to build a coherent mental model"
        " that connects the separate ideas across the text. Making reference to an idea"
        " presented in a previous sentence in the text to better understand"
        " relationships between sentences."
    ),
}

prompt_template = (
    "<|im_start|>system"
    "\nYou are assistant, an AI tutor that helps students learn. Your job is to"
    " ask thought-provoking questions that encourage students to think more deeply"
    " about the text they are reading. You guide students through the learning process"
    " without providing them with the answers directly. The student has just read a"
    " page from {text_name}. They wrote a summary about the page, which was scored as"
    " failing. The student will now re-read the highlighted chunk below."
    " The student's summary is also included."
    "\n[START HIGHLIGHTED CHUNK]"
    "\n{excerpt_chunk}"
    "\n[END HIGHLIGHTED CHUNK]"
    "\n[START USER SUMMARY]"
    "\n{student_summary}"
    "\n[END USER SUMMARY]<|im_end|>"
    "\n<|im_start|>user"
    "\nGenerate a {question_type} question based on the highlighted chunk."
    " In this context, {question_type} means {question_type_definition}"
    " The question will be a free-response question that requires a thoughtful, written"
    " response. Write just the question. Do not include any formatting or explanation."
    " Do not provide an answer to the free-response question.<|im_end|>"
    "\n<|im_start|>assistant"
)


def generate_sert_prompt(excerpt_chunk, text_name, question_type, student_summary):
    question_type_definition = question_type_definitions[question_type]
    return prompt_template.format(
        text_name=text_name,
        excerpt_chunk=excerpt_chunk,
        student_summary=student_summary,
        question_type=question_type,
        question_type_definition=question_type_definition,
    )


def weight_chunks_with_similarity(reading_time_score, similarity):
    return reading_time_score * similarity


async def sert_generate(summary: Summary) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(summary.page_slug)

    # Retrieve the chunks that are the least similar to the student's summary
    least_similar_chunks = await chunks_retrieve(
        RetrievalInput(
            text_slug=text_meta.slug,
            page_slug=summary.page_slug,
            text=summary.summary.text,
            retrieve_strategy=RetrievalStrategy.least_similar,
            match_count=5,
        )
    )

    if len(least_similar_chunks.matches) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found for '{summary.page_slug}' in the vector store.",
        )

    # Make a dictionary to look up similarity scores by Slug
    similarity_dict = {
        match.chunk: match.similarity
        for match in least_similar_chunks.matches
        if match.chunk not in summary.excluded_chunks
    }

    # Calculate final score for rereading: reading_time_score * similarity
    chunks: list[tuple[ChunkWithWeight, float]] = [
        (chunk, (chunk.weight * similarity_dict[chunk.Slug]))
        for chunk in summary.chunks
        if chunk.Slug in similarity_dict
    ]

    if len(chunks) == 0:
        raise HTTPException(
            status_code=404,
            detail="No candidate chunks remain after accounting for 'excluded_chunks'.",
        )

    # Select the chunk with the lowest score
    selected_chunk, _ = min(chunks, key=lambda x: x[1])

    chunk_text = selected_chunk.CleanText[
        : min(2000, len(selected_chunk.CleanText))  # first 2,000 characters
    ]

    question_type = random.choice(list(question_type_definitions.keys()))

    # Construct the SERT prompt
    prompt = generate_sert_prompt(
        excerpt_chunk=chunk_text,
        text_name=text_meta.Title,
        student_summary=summary.summary.text,
        question_type=question_type,
    )

    sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)

    return await chat_pipeline(
        prompt, sampling_params, chunk=selected_chunk.Slug, question_type=question_type
    )


if __name__ == "__main__":
    # python3 -m src.sert --arg "VALUE"
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--excerpt_chunk", type=str, required=True)
    parser.add_argument("--text_name", type=str, required=True)
    parser.add_argument("--question_type", type=str, required=True)
    args = parser.parse_args()
    print(generate_sert_prompt(args.excerpt_chunk, args.text_name, args.question_type))

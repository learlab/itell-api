from typing import AsyncGenerator

from fastapi import HTTPException
from jinja2 import Template
from vllm.sampling_params import SamplingParams

from src.dependencies.faiss import FAISS_Wrapper

from ..dependencies.strapi import Strapi
from ..pipelines.chat import chat_pipeline
from ..schemas.chat import (
    ChatInput,
    ChatInputCRI,
    ChatInputSERT,
    ChatInputThinkAloud,
    EventType,
    PromptInput,
)
from ..schemas.embedding import Match, RetrievalInput
from ..schemas.strapi import Chunk


def get_template(file_path: str) -> Template:
    with open(file_path, "r", encoding="utf8") as file_:
        return Template(file_.read())


moderated_chat_template = get_template("templates/chat.jinja2")
sert_followup_template = get_template("templates/sert_followup.jinja2")
sert_final_template = get_template("templates/sert_final.jinja2")
think_aloud_followup_template = get_template("templates/think_aloud_followup.jinja2")
think_aloud_final_template = get_template("templates/think_aloud_final.jinja2")
cri_prompt_template = get_template("templates/cri_chat.jinja2")

sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)


def choose_relevant_chunk(
    relevant_chunks: list[Match], current_chunk: str | None
) -> Match | None:
    if not relevant_chunks:
        return None

    relevant_chunk_dict = {match.chunk: match for match in relevant_chunks}

    if current_chunk and current_chunk in relevant_chunk_dict:
        return relevant_chunk_dict[current_chunk]
    else:
        return max(relevant_chunks, key=lambda match: match.similarity)


async def moderated_chat(
    chat_input: ChatInput,
    strapi: Strapi,
    faiss: FAISS_Wrapper,
) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    relevant_chunks = await faiss.retrieve_chunks(
        RetrievalInput(
            text_slug=text_meta.slug,
            page_slugs=[chat_input.page_slug, "user-guide-baseline"],
            text=chat_input.message,
            similarity_threshold=0.15,
            match_count=10,
        )
    )

    relevant_chunk = choose_relevant_chunk(
        relevant_chunks.matches, chat_input.current_chunk
    )

    if relevant_chunk and relevant_chunk.page == "user-guide-baseline":
        text_name = "iTELL User Guide"
        text_info = "iTELL stands for intelligent texts for enhanced lifelong learning. It is a platform that provides students with a personalized learning experience. This user guide provides information on how to navigate the iTELL platform."  # noqa: E501
        cited_chunk = "[User Guide]"
    else:
        text_name = text_meta.title
        text_info = text_meta.description
        cited_chunk = relevant_chunk.chunk if relevant_chunk else None

    # Get last 4 messages from chat history
    chat_history = [(msg.agent, msg.text) for msg in chat_input.history[-4:]]

    prompt = moderated_chat_template.render(
        text_name=text_name,
        text_info=text_info,
        context=relevant_chunk.content if relevant_chunk else None,
        chat_history=chat_history,
        user_message=chat_input.message,
        student_summary=chat_input.summary,
    )

    return await chat_pipeline(
        prompt,
        sampling_params,
        event_type=EventType.chat,
        context=[cited_chunk] if cited_chunk else None,
    )


async def unmoderated_chat(raw_chat_input: PromptInput) -> AsyncGenerator[bytes, None]:
    return await chat_pipeline(
        raw_chat_input.message,
        sampling_params,
        event_type=EventType.chat,
    )


# SERT
async def sert_followup(
    chat_input: ChatInputSERT, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(chat_input.page_slug)
    current_chunk: Chunk = await strapi.get_chunk(
        chat_input.page_slug, chat_input.current_chunk
    )

    try:
        sert_question = chat_input.history[0].text
    except IndexError:
        raise HTTPException(status_code=400, detail="No SERT question found in history")

    prompt = sert_followup_template.render(
        text_name=text_meta.title,
        text_info=text_meta.description,
        context=current_chunk.clean_text,
        sert_question=sert_question,
        learner_response=chat_input.message
    )

    return await chat_pipeline(prompt, sampling_params, event_type=EventType.chat)


async def sert_final(
    chat_input: ChatInputSERT, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(chat_input.page_slug)
    current_chunk: Chunk = await strapi.get_chunk(
        chat_input.page_slug, chat_input.current_chunk
    )

    prompt = sert_final_template.render(
        text_name=text_meta.title,
        text_info=text_meta.description,
        context=current_chunk.clean_text,
        chat_history=chat_input.history,
        user_message=chat_input.message,
        student_summary=chat_input.summary,
    )

    return await chat_pipeline(prompt, sampling_params, event_type=EventType.chat)


# Think Aloud
async def think_aloud_followup(
    chat_input: ChatInputThinkAloud, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    prompt = think_aloud_followup_template.render(
        text_name=text_meta.title,
        text_info=text_meta.description,
        chat_history=chat_input.history,
        user_message=chat_input.message,
    )

    return await chat_pipeline(prompt, sampling_params, event_type=EventType.chat)


async def think_aloud_final(
    chat_input: ChatInputThinkAloud, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    prompt = think_aloud_final_template.render(
        text_name=text_meta.title,
        chat_history=chat_input.history,
        user_message=chat_input.message,
    )

    return await chat_pipeline(prompt, sampling_params, event_type=EventType.chat)


# CRI Feedback
async def cri_chat(
    cri_input: ChatInputCRI, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    chunk = await strapi.get_chunk(cri_input.page_slug, cri_input.chunk_slug)
    text_meta = await strapi.get_text_meta(cri_input.page_slug)

    target_properties = ["constructed_response", "question", "clean_text"]

    for prop in target_properties:
        if getattr(chunk, prop) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Requested Chunk does not have {prop}",
            )

    prompt = cri_prompt_template.render(
        text_name=text_meta.title,
        clean_text=chunk.clean_text,
        question=chunk.question,
        golden_answer=chunk.constructed_response,
        student_response=cri_input.student_response,
    )

    return await chat_pipeline(
        prompt,
        sampling_params,
        event_type=EventType.constructed_response_feedback,
    )

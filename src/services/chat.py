from typing import AsyncGenerator

from fastapi import HTTPException
from jinja2 import Template
from vllm.sampling_params import SamplingParams

from ..dependencies.strapi import Strapi
from ..dependencies.supabase import SupabaseClient
from ..pipelines.chat import chat_pipeline
from ..schemas.chat import (
    ChatInput,
    ChatInputCRI,
    ChatInputSERT,
    EventType,
    PromptInput,
)
from ..schemas.embedding import Match, RetrievalInput
from ..schemas.strapi import Chunk
from ..schemas.summary import Summary

with open("templates/chat.jinja2", "r", encoding="utf8") as file_:
    prompt_template = Template(file_.read())

with open("templates/cri_chat.jinja2", "r", encoding="utf8") as file_:
    cri_prompt_template = Template(file_.read())

with open("templates/language_feedback.jinja2", "r", encoding="utf8") as file_:
    language_feedback_template = Template(file_.read())

sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)


def choose_relevant_chunk(relevant_chunks: list[Match], current_chunk: str):
    if len(relevant_chunks.matches) == 0:
        return None

    relevant_chunk_dict = {match.chunk: match for match in relevant_chunks.matches}

    if current_chunk in relevant_chunk_dict:
        return relevant_chunk_dict[current_chunk]
    else:
        return relevant_chunks.matches[0]


async def moderated_chat(
    chat_input: ChatInput,
    strapi: Strapi,
    supabase: SupabaseClient,
) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    relevant_chunks = await supabase.retrieve_chunks(
        RetrievalInput(
            text_slug=text_meta.Slug,
            page_slugs=[chat_input.page_slug, "itell-documentation"],
            text=chat_input.message,
            similarity_threshold=0.15,
            match_count=10,
        )
    )

    relevant_chunk = choose_relevant_chunk(relevant_chunks, chat_input.current_chunk)

    if relevant_chunk and relevant_chunk.page == "itell-documentation":
        text_name = "iTELL Documentation"
        text_info = "iTELL stands for intelligent texts for enhanced lifelong learning. It is a platform that provides students with a personalized learning experience. This user guide provides information on how to navigate the iTELL platform."  # noqa: E501
    else:
        text_name = text_meta.Title
        text_info = text_meta.Description

    # Get last 4 messages from chat history
    chat_history = [(msg.agent, msg.text) for msg in chat_input.history[-4:]]

    prompt = prompt_template.render(
        text_name=text_name,
        text_info=text_info,
        context=relevant_chunk.content if relevant_chunk else None,
        chat_history=chat_history,
        user_message=chat_input.message,
        student_summary=chat_input.summary,
    )

    if relevant_chunk.page == "itell-documentation":
        cited_chunk = "[User Guide]"
    else:
        cited_chunk = relevant_chunk.chunk

    return await chat_pipeline(
        prompt, sampling_params, event_type=EventType.chat, context=cited_chunk
    )


async def unmoderated_chat(raw_chat_input: PromptInput) -> AsyncGenerator[bytes, None]:
    return await chat_pipeline(
        raw_chat_input.message,
        sampling_params,
        event_type=EventType.chat,
    )


async def sert_chat(
    chat_input: ChatInputSERT, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(chat_input.page_slug)
    current_chunk: Chunk = await strapi.get_chunk(
        chat_input.page_slug, chat_input.current_chunk
    )

    # Get last 4 messages from chat history
    chat_history = [(msg.agent, msg.text) for msg in chat_input.history[-4:]]

    prompt = prompt_template.render(
        text_name=text_meta.Title,
        text_info=text_meta.Description,
        context=current_chunk.CleanText,
        chat_history=chat_history,
        user_message=chat_input.message,
        student_summary=chat_input.summary,
    )

    return await chat_pipeline(prompt, sampling_params, event_type=EventType.chat)


async def cri_chat(
    cri_input: ChatInputCRI, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    chunk = await strapi.get_chunk(cri_input.page_slug, cri_input.chunk_slug)
    text_meta = await strapi.get_text_meta(cri_input.page_slug)

    target_properties = ["ConstructedResponse", "Question", "CleanText"]

    for prop in target_properties:
        if getattr(chunk, prop) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Requested Chunk does not have {prop}",
            )

    prompt = cri_prompt_template.render(
        text_name=text_meta.Title,
        clean_text=chunk.CleanText,
        question=chunk.Question,
        golden_answer=chunk.ConstructedResponse,
        student_response=cri_input.student_response,
    )

    return await chat_pipeline(
        prompt,
        sampling_params,
        event_type=EventType.constructed_response_feedback,
    )


async def language_feedback_chat(
    summary: Summary, strapi: Strapi
) -> AsyncGenerator[bytes, None]:
    text_meta = await strapi.get_text_meta(summary.page_slug)

    prompt = language_feedback_template.render(
        text_name=text_meta.Title,
        summary=summary.summary.text,
    )

    return await chat_pipeline(
        prompt, sampling_params, event_type=EventType.language_feedback
    )

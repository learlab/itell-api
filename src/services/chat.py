from typing import AsyncGenerator

from fastapi import HTTPException
from jinja2 import Template
from vllm.sampling_params import SamplingParams

from ..dependencies.faiss import FAISS_Wrapper
from ..dependencies.strapi import Strapi
from ..dependencies.supabase import SupabaseClient
from ..pipelines.chat import chat_pipeline
from ..schemas.chat import ChatInput, ChatInputCRI, EventType, PromptInput
from ..schemas.embedding import RetrievalInput
from ..schemas.summary import Summary

with open("templates/chat.jinja2", "r", encoding="utf8") as file_:
    prompt_template = Template(file_.read())

with open("templates/cri_chat.jinja2", "r", encoding="utf8") as file_:
    cri_prompt_template = Template(file_.read())

with open("templates/language_feedback.jinja2", "r", encoding="utf8") as file_:
    language_feedback_template = Template(file_.read())

sampling_params = SamplingParams(temperature=0.4, max_tokens=4096)


async def moderated_chat(
    chat_input: ChatInput,
    strapi: Strapi,
    faiss: FAISS_Wrapper,
) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    relevant_chunks = await faiss.retrieve_chunks(
        RetrievalInput(
            text_slug=text_meta.Slug,
            page_slugs=[chat_input.page_slug, "itell-documentation"],
            text=chat_input.message,
            similarity_threshold=1.3,
            match_count=1,
        )
    )

    if len(relevant_chunks.matches) > 0:
        relevant_chunk = relevant_chunks.matches[0]
    else:
        relevant_chunk = None

    if relevant_chunk and relevant_chunk.page == "itell-documentation":
        text_name = "iTELL Documentation"
        text_info = "iTELL stands for intelligent texts for enhanced lifelong learning. It is a platform that provides students with a personalized learning experience. This user guide provides information on how to navigate the iTELL platform."  # noqa: E501
    else:
        text_name = text_meta.Title
        text_info = text_meta.Description

    # TODO: Retrieve Examples
    # We can set up a database of a questions and responses
    # that the bot will use as a reference.

    # Get last 4 messages from chat history
    chat_history = chat_input.history[-4:]

    prompt = prompt_template.render(
        text_name=text_name,
        text_info=text_info,
        context=relevant_chunk.content if relevant_chunk else None,
        chat_history=[(msg.agent, msg.text) for msg in chat_history],
        user_message=chat_input.message,
        student_summary=chat_input.summary,
    )

    cited_chunks = [
        match.chunk if match.page != "itell-documentation" else "[User Guide]"
        for match in relevant_chunks.matches
    ]

    return await chat_pipeline(
        prompt, sampling_params, event_type=EventType.chat, context=cited_chunks
    )


async def unmoderated_chat(raw_chat_input: PromptInput) -> AsyncGenerator[bytes, None]:
    return await chat_pipeline(
        raw_chat_input.message,
        sampling_params,
        event_type=EventType.chat,
    )


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

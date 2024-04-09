# flake8: noqa E501
from .models.chat import ChatInput, PromptInput, ChatInputCRI
from .models.embedding import RetrievalInput
from typing import AsyncGenerator
from .embedding import chunks_retrieve
from .pipelines.chat import chat_pipeline, chat_CRI_pipeline
from .connections.strapi import Strapi

from jinja2 import Template
from vllm.sampling_params import SamplingParams

strapi = Strapi()

with open("templates/chat.jinja2", "r", encoding="utf8") as file_:
    prompt_template = Template(file_.read())

with open("templates/cri_chat.jinja2", "r", encoding="utf8") as file_:
    cri_prompt_template = Template(file_.read())

async def moderated_chat(chat_input: ChatInput) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    relevant_chunks = await chunks_retrieve(
        RetrievalInput(
            text_slug=text_meta.slug,
            page_slug=chat_input.page_slug,
            text=chat_input.message,
            similarity_threshold=0.2,
            match_count=1,
        )
    )

    # TODO: Retrieve Examples
    # We can set up a database of a questions and responses
    # that the bot will use as a reference.

    prompt = prompt_template.render(
        text_name=text_meta.Title,
        text_info=text_meta.Description,
        context=relevant_chunks.matches,
        chat_history=[(msg.agent, msg.text) for msg in chat_input.history],
        user_message=chat_input.message,
        student_summary=chat_input.summary,
    )

    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=4096, stop=["<|im_end|>"]
    )

    cited_chunks = [chunk.chunk for chunk in relevant_chunks.matches]

    return await chat_pipeline(prompt, sampling_params, context=cited_chunks)


async def unmoderated_chat(raw_chat_input: PromptInput) -> AsyncGenerator[bytes, None]:
    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=4096, stop=["<|im_end|>"]
    )
    return await chat_pipeline(raw_chat_input.message, sampling_params)

async def cri_chat(cri_input: ChatInputCRI) -> AsyncGenerator[bytes, None]:
    chunk = await strapi.get_chunk(
        cri_input.page_slug, cri_input.chunk_slug
    )

    target_properties = ['ConstructedResponse', 'Question', 'CleanText']

    for prop in target_properties:
        if getattr(chunk, prop) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Requested Chunk does not have {prop}",
            )

    prompt = cri_prompt_template.render(
        clean_text=chunk.CleanText,
        question=chunk.Question,
        golden_answer=chunk.ConstructedResponse,
        student_response=cri_input.student_response
    )

    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=4096, stop=["<|im_end|>"]
    )
    return await chat_CRI_pipeline(prompt, sampling_params)

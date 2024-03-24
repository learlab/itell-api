# flake8: noqa E501
from .models.chat import ChatInput, PromptInput
from .models.embedding import RetrievalInput
from typing import AsyncGenerator
from .embedding import chunks_retrieve
from .pipelines.chat import chat_pipeline
from .connections.strapi import Strapi

from jinja2 import Template
from vllm.sampling_params import SamplingParams

strapi = Strapi()

with open("templates/chat.jinja2", "r", encoding="utf8") as file_:
    prompt_template = Template(file_.read())

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
        chat_history=chat_input.history,
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

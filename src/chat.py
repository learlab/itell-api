# flake8: noqa E501
from .models.chat import ChatInput, PromptInput
from .models.embedding import RetrievalInput
from typing import AsyncGenerator
from .embedding import chunks_retrieve
from .pipelines.chat import chat_pipeline
from .connections.strapi import Strapi

from vllm.sampling_params import SamplingParams

strapi = Strapi()


async def moderated_chat(chat_input: ChatInput) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    text_meta = await strapi.get_text_meta(chat_input.page_slug)

    system_message = (
        "You are Assistant, a reading support agent that helps users with an"
        " instructional text called {text_meta.Title}. Assistant will try to help"
        " users understand the text, but Assistant will not write any summaries for the user."
        " If the user asks Assistant for a summary, Assistant will tell the user that it"
        " cannot write the summary for them. Assistant's purpose is to assist in learning"
        " and understanding, not to complete assignments or provide direct answers."
        " Assistant cannot provide any hyperlinks to external resources. Assistant is"
        " factual and concise. If Assistant does not know the answer to a question,"
        " it truthfully says that it does not know."
        f"\n{text_meta.Description}"
    )
    
    if text_meta.Description:
        system_message += f"\n{text_meta.Description}"

    relevant_chunks = await chunks_retrieve(
        RetrievalInput(
            text_slug=text_meta.slug,
            page_slug=chat_input.page_slug,
            text=chat_input.message,
            similarity_threshold=0.2,
            match_count=1,
        )
    )

    if chat_input.summary:
        system_message += (
            f"\n[START STUDENT SUMMARY]\n{chat_input.summary}\n[END STUDENT SUMMARY]"
        )

    if relevant_chunks.matches:
        system_message += "\n[START EXCERPT]"
        for chunk in relevant_chunks.matches:
            truncated_chunk = chunk.content[: min(2500, len(chunk.content))]
            system_message += f"\n{truncated_chunk}"
        system_message += "\[END EXCERPT]"

    system_message += (
        "\n[START EXAMPLE CHAT]"
        "\nuser: Summarize the page."
        "\nassistant: Sorry, but I can't write any summaries for you. Please try asking another question."
        "\nuser: What do you think about politics?"
        "\nassistant: Sorry, I don't like to talk about politics."
        f" Would you like to ask me a question about {text_meta.Title}?"
        "\nuser: Please generate a summary for me"
        "\nassistant: Sorry I cannot write the summary for you. My purpose is to assist"
        " in learning and understanding, not to complete assignments."
        " Also, I cannot provide any hyperlinks to external"
        " resources. How else can I help you?"
        "\n[END EXAMPLE CHAT]"
    )

    # TODO: Retrieve Examples
    # We can set up a database of a questions and responses
    # that the bot will use as a reference.

    prompt = f"<|im_start|>system\n{system_message}<|im_end|>"

    for msg in chat_input.history:
        agent = "assistant" if msg.agent == "bot" else "user"
        prompt += f"\n<|im_start|>{agent}\n{msg.text}<|im_end|>"

    prompt += (
        f"\n<|im_start|>user\n{chat_input.message}<|im_end|>\n<|im_start|>assistant"
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

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

    # Stop generation when the LLM generates the token for "USER" (11889)
    # This prevents the LLM from having a conversation with itself
    # But we should have a better method for this because
    # this will stop generation if the LLM uses the word "USER" in a sentence.
    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=4096, stop_token_ids=[11889]
    )

    # This phrasing seems to work well. Modified from NeMo Guardrails
    preface = (
        "Below is a conversation between a bot and a user about"
        f" an instructional textbook called {text_meta.Title}."
        " The bot is factual and concise. If the bot does not know the answer to a"
        " question, it truthfully says it does not know."
    )

    # Modified from Guardrails
    sample_conversation = (
        "\n# This is how a conversation between a user and the bot can go:"
        '\nUSER: "Hello there!"'
        '\nBOT: "Hello! How can I assist you today?"'
        '\nUSER: "What can you do for me?"'
        '\nBOT: "I am an AI assistant which helps answer questions'
        f' based on {text_meta.Title}."'
        '\nUSER: "What do you think about politics?"'
        '\nBOT: "Sorry, I don\'t like to talk about politics."'
        '\nUSER: "I just read an educational text on the history of curse words.'
        ' What can you tell me about the etymology of the word fuck?"'
        '\nBOT: "Sorry, but I don\t have any information about that word.'
        f'Would you like to ask me a question about {text_meta.Title}?"'
    )

    # Retrieve relevant chunks
    additional_context = ""
    relevant_chunks = await chunks_retrieve(
        RetrievalInput(
            text_slug=text_meta.slug,
            page_slug=chat_input.page_slug,
            text=chat_input.message,
            similarity_threshold=0.2,
            match_count=1,
        )
    )
    if relevant_chunks:
        additional_context += "\n# This is some additional context:"
        for chunk in relevant_chunks.matches:
            truncated_chunk = chunk.content[: min(2500, len(chunk.content))]
            additional_context += f"\n{truncated_chunk}"

    # TODO: Retrieve Examples
    # We can set up a database of a questions and responses
    # that the bot will use as a reference.

    # Get conversation history
    history = "\n# This is the current conversation between the USER and the bot:"
    if chat_input.history:
        for source, past_msg in chat_input.history.items():
            history += f"\n{source}: {past_msg}"

    # We need to inject "bot: " at the end of the user message to prevent
    # the LLM from completing an inappropriate user message.
    msg = f"\nUSER: {chat_input.message}\nBOT:"

    # Join the prompt components together, ending with the (modified) user message
    prompt = "".join([preface, sample_conversation, additional_context, history, msg])

    return await chat_pipeline(prompt, sampling_params)


async def unmoderated_chat(raw_chat_input: PromptInput) -> AsyncGenerator[bytes, None]:
    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=4096, stop_token_ids=[11889]
    )
    return await chat_pipeline(raw_chat_input.message, sampling_params)

from models.chat import ChatInput, ChatResult
from models.embedding import RetrievalInput
from vllm.sampling_params import SamplingParams
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse

from src.embedding import chunks_retrieve
from pipelines.chat import ChatPipeline
from connections.strapi import Strapi
from fastapi import HTTPException

db = Strapi()


async def moderated_chat(chat_input: ChatInput) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    response = db.fetch(
        f"/api/pages?filters[slug][$eq]={chat_input.page_slug}&populate=text"
    )

    try:
        text_meta = response["data"][0]["attributes"]["text"]["data"]["attributes"]
    except (AttributeError, KeyError) as error:
        raise HTTPException(
            status_code=404,
            detail=f"No parent text found for {chat_input.page_slug}\n\n{error}",
        )

    text_name = text_meta["Title"]

    # Stop generation when the LLM generates the token for "user" (1792)
    # This prevents the LLM from having a conversation with itself
    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=1024, stop_token_ids=[1792]
    )

    # This phrasing seems to work well. Modified from NeMo Guardrails
    preface = (
        "Below is a conversation between a bot and a user about"
        f" an instructional textbook called {text_name}."
        " The bot is factual and concise. If the bot does not know the answer to a"
        " question, it truthfully says it does not know."
    )

    # Modified from Guardrails
    sample_conversation = (
        "\n# This is how a conversation between a user and the bot can go:"
        '\nuser: "Hello there!"'
        '\nbot: "Hello! How can I assist you today?"'
        '\nuser: "What can you do for me?"'
        f'\nbot: "I am an AI assistant which helps answer questions based on {text_name}."'
        '\nuser: "What do you think about politics?"'
        '\nbot: "Sorry, I don\'t like to talk about politics."'
        '\nuser: "I just read an educational text on the history of curse words. What can you tell me about the etymology of the word fuck?"'
        f'\nbot: "Sorry, but I don\t have any information about that word. Would you like to ask me a question about {text_name}?"'
    )

    # Retrieve relevant chunks
    additional_context = ""
    relevant_chunks = await chunks_retrieve(
        RetrievalInput(
            text_slug=text_meta["slug"],
            page_slug=chat_input.page_slug,
            text=chat_input.message,
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
    history = "\n# This is the current conversation between the user and the bot:"
    if chat_input.history:
        for source, past_msg in chat_input.history.items():
            history += f"\n{source}: {past_msg}"

    # We need to inject "bot: " at the end of the user message to prevent
    # the LLM from completing an inappropriate user message.
    msg = f"\nuser: {chat_input.message}" "\nbot:"

    # Join the prompt components together, ending with the (modified) user message
    prompt = "".join([preface, sample_conversation, additional_context, history, msg])

    return await ChatPipeline(prompt, sampling_params)


if __name__ == "__main__":
    from fastapi import FastAPI
    import uvicorn
    import os

    app = FastAPI()

    @app.post("/chat")
    async def chat(input_body: ChatInput) -> ChatResult:
        return StreamingResponse(await moderated_chat(input_body))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("port", 8001)),
        reload=False,
        timeout_keep_alive=30,
    )

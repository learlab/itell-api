from models.chat import ChatInput, ChatResult
from models.embedding import RetrievalInput
from vllm.sampling_params import SamplingParams
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse

from src.embedding import chunks_retrieve
from pipelines.chat import ChatPipeline


async def moderated_chat(chat_input: ChatInput) -> AsyncGenerator[bytes, None]:
    # Adding in the specific name of the textbook majorly improved response quality
    textbook_name = chat_input.text_slug

    # Stop generation when the LLM generates the token for "user" (1792)
    # This prevents the LLM from having a conversation with itself
    sampling_params = SamplingParams(
        temperature=0.4, max_tokens=1024, stop_token_ids=[1792]
    )

    # This phrasing seems to work well. Modified from NeMo Guardrails
    preface = (
        "Below is a conversation between a bot and a user about"
        f" an instructional textbook called {textbook_name}."
        " The bot is factual and concise. If the bot does not know the answer to a"
        " question, it truthfully says it does not know."
    )

    # Modified from Guardrails
    sample_conversation = (
        "\n# This is how a conversation between a user and the bot can go:"
        '\nuser: "Hello there!"'
        '\nbot: "Hello! How can I assist you today?"'
        '\nuser: "What can you do for me?"'
        f'\nbot: "I am an AI assistant which helps answer questions based on {textbook_name}."'
        '\nuser: "What do you think about politics?"'
        '\nbot: "Sorry, I don\'t like to talk about politics."'
        '\nuser: "I just read an educational text on the history of curse words. What can you tell me about the etymology of the word fuck?"'
        f'\nbot: "Sorry, but I don\t have any information about that word. Would you like to ask me a question about {textbook_name}?"'
    )

    # Retrieve relevant chunks
    additional_context = ""
    # changing the input parameter from providing db to including `textbook_name` in `input_body` as `text` to filter chunks in the database
    relevant_chunks = await chunks_retrieve(
        RetrievalInput(page_slug=textbook_name, text=chat_input.message, match_count=1)
    )
    if relevant_chunks:
        additional_context += "\n# This is some additional context:"
        for chunk in relevant_chunks.matches:
            additional_context += f"\n{chunk.content}"

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

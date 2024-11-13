from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..logging.logging_router import LoggingRoute, LoggingStreamingResponse
from ..schemas.chat import (
    ChatInput,
    ChatInputCRI,
    ChatInputSERT,
    ChatInputThinkAloud,
    PromptInput,
)
from ..services.chat import (
    cri_chat,
    moderated_chat,
    sert_final,
    sert_followup,
    think_aloud_final,
    think_aloud_followup,
    unmoderated_chat,
)
from ..services.stairs import think_aloud

router = APIRouter(route_class=LoggingRoute)


@router.post("/chat")
async def chat(
    input_body: ChatInput,
    request: Request,
) -> StreamingResponse:
    """Responds to user queries incorporating relevant chunks from the current page.

    The response is a StreamingResponse wih the following fields:
    - **request_id**: a unique identifier for the request
    - **text**: the response text
    """
    strapi = request.app.state.strapi
    faiss = request.app.state.faiss
    chat_stream = await moderated_chat(input_body, strapi, faiss)

    return LoggingStreamingResponse(content=chat_stream, media_type="text/event-stream")


@router.post("/chat/raw")
async def raw_chat(input_body: PromptInput) -> StreamingResponse:
    """Direct access to the underlying chat model.
    For testing purposes.
    """
    return StreamingResponse(
        content=await unmoderated_chat(input_body), media_type="text/event-stream"
    )


@router.post("/chat/CRI")
async def chat_cri(
    input_body: ChatInputCRI,
    request: Request,
) -> StreamingResponse:
    """Explains why a student's response to a constructed response item
    was evaluated as incorrect
    """
    strapi = request.app.state.strapi
    chat_stream = await cri_chat(input_body, strapi)
    return LoggingStreamingResponse(content=chat_stream, media_type="text/event-stream")


@router.post("/chat/sert")
async def chat_sert(
    input_body: ChatInputSERT,
    request: Request,
) -> StreamingResponse:
    """Responds to user queries incorporating the current in-focus chunk.

    The response is a StreamingResponse wih the following fields:
    - **request_id**: a unique identifier for the request
    - **text**: the response text
    """
    strapi = request.app.state.strapi

    if not input_body.history:
        raise HTTPException(
            status_code=422,
            detail="History must be provided to continue a SERT chat.",
        )
    elif len(input_body.history) == 1:
        chat_stream = await sert_followup(input_body, strapi)
    elif len(input_body.history) == 3:
        chat_stream = await sert_final(input_body, strapi)

    return LoggingStreamingResponse(content=chat_stream, media_type="text/event-stream")


@router.post("/chat/think_aloud")
async def chat_think_aloud(
    input_body: ChatInputThinkAloud,
    request: Request,
) -> StreamingResponse:
    """Generates a think aloud protocol from the provided chunk.

    The response is a StreamingResponse wih the following fields:
    - **request_id**: a unique identifier for the request
    - **text**: the response text
    """
    strapi = request.app.state.strapi
    if not input_body.history:
        chat_stream = await think_aloud(input_body, strapi)
    elif len(input_body.history) == 1:
        chat_stream = await think_aloud_followup(input_body, strapi)
    elif len(input_body.history) == 3:
        chat_stream = await think_aloud_final(input_body, strapi)

    return LoggingStreamingResponse(content=chat_stream, media_type="text/event-stream")

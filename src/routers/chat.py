from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ..logging.logging_router import LoggingRoute, LoggingStreamingResponse
from ..schemas.chat import ChatInput, ChatInputCRI, ChatInputSTAIRS, PromptInput
from ..services.chat import (
    cri_chat,
    moderated_chat,
    sert_chat,
    stairs_chat,
    unmoderated_chat,
)

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
    supabase = request.app.state.supabase
    chat_stream = await moderated_chat(input_body, strapi, supabase)

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


@router.post("/chat/SERT")
async def chat_sert(
    input_body: ChatInputSTAIRS,
    request: Request,
) -> StreamingResponse:
    """Responds to user queries incorporating the current in-focus chunk.

    The response is a StreamingResponse wih the following fields:
    - **request_id**: a unique identifier for the request
    - **text**: the response text
    """
    strapi = request.app.state.strapi
    chat_stream = await sert_chat(input_body, strapi)

    return LoggingStreamingResponse(content=chat_stream, media_type="text/event-stream")


@router.post("/chat/STAIRS")
async def chat_stairs(
    input_body: ChatInputSTAIRS,
    request: Request,
) -> StreamingResponse:
    """Responds to user queries incorporating the current in-focus chunk.

    The response is a StreamingResponse wih the following fields:
    - **request_id**: a unique identifier for the request
    - **text**: the response text
    """
    strapi = request.app.state.strapi
    chat_stream = await stairs_chat(input_body, strapi)

    return LoggingStreamingResponse(content=chat_stream, media_type="text/event-stream")

from fastapi.responses import StreamingResponse
from ..models.chat import ChatInput, PromptInput, ChatInputCRI
from ..chat import moderated_chat, unmoderated_chat, cri_chat
from .dependencies.supabase import SupabaseDep
from .dependencies.strapi import StrapiDep
from fastapi import APIRouter
from .logging_router import LoggingRoute

router = APIRouter(route_class=LoggingRoute)


@router.post("/chat")
async def chat(
    input_body: ChatInput,
    strapi: StrapiDep,
    supabase: SupabaseDep,
) -> StreamingResponse:
    """Responds to user queries incorporating relevant chunks from the current page.

    The response is a StreamingResponse wih the following fields:
    - **request_id**: a unique identifier for the request
    - **text**: the response text
    """
    chat_stream = await moderated_chat(input_body, strapi, supabase)

    return StreamingResponse(content=chat_stream, media_type="text/event-stream")


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
    strapi: StrapiDep,
) -> StreamingResponse:
    """Explains why a student's response to a constructed response item
    was evaluated as incorrect
    """
    chat_stream = await cri_chat(input_body, strapi)
    return StreamingResponse(content=chat_stream, media_type="text/event-stream")

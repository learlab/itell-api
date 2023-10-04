from models.chat import ChatInput, ChatResult
from pipelines.chat import ChatPipeline

async def moderated_chat(input_body: ChatInput) -> ChatResult:
    result = await rails.generate_async(input_body.message)
    if isinstance(result, str):
        # TODO: Add required ChatResult fields.
        return ChatResult(message=result)
    else:
        return ChatResult(message="Internal Server Error")
from nemoguardrails import LLMRails, RailsConfig
from models.chat import ChatInput, ChatResult

# initialize rails config
config = RailsConfig.from_path("guardrails/vicuna-7b")
# create rails
rails = LLMRails(config, verbose=False)


async def moderated_chat(input_body: ChatInput) -> ChatResult:
    result = await rails.generate_async(input_body.message)
    if isinstance(result, str):
        return ChatResult(message=result)
    else:
        return ChatResult(message="Internal Server Error")


if __name__ == "__main__":
    print(rails.registered_actions)  # type: ignore

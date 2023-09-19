from nemoguardrails import LLMRails, RailsConfig
from models.chat import ChatInput, ChatResult

# initialize rails
config = RailsConfig.from_path("guardrails/open-orca")
rails = LLMRails(config, verbose=False)


async def moderated_chat(input_body: ChatInput) -> ChatResult:
    result = await rails.generate_async(input_body.message)
    if isinstance(result, str):
        # TODO: Add required ChatResult fields.
        return ChatResult(message=result)
    else:
        return ChatResult(message="Internal Server Error")


if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            print("Assistant: ", end="")
            response = rails.generate(user_input)
            print(response)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
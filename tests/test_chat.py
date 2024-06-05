from src.models.chat import ChatResponse, EventType
from pydantic import ValidationError


async def test_chat(client):
    async with client.stream(
        "POST",
        "/chat",
        json={
            "page_slug": "emotional",
            "message": "What are emotions about?",
        },
    ) as response:
        assert response.status_code == 200

        # We need to simulate the streaming response due to an issue with
        # Starlette's TestClient https://github.com/encode/starlette/issues/1102
        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        # The first chunk is the feedback
        first_chunk = next(stream).removeprefix(f"event: {EventType.chat}\ndata: ")

        # Checks that the first chunk is a valid ChatResponse object.
        try:
            message = ChatResponse.model_validate_json(first_chunk)
        except ValidationError as err:
            print(err)
            raise

    # Check that a chunk was cited
    assert len(message.context) != 0, "A chunk should be cited."

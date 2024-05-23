import pytest
import os
from src.models.chat import ChatResponse
from pydantic import ValidationError


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_chat(client):
    response = await client.post(
        "/chat",
        json={
            "page_slug": "what-is-law",
            "message": "I don't understand how legal systems actually help anyone.",
        },
    )
    assert response.status_code == 200

    # We need to simulate the streaming response due to an issue with
    # Starlette's TestClient https://github.com/encode/starlette/issues/1102
    first_response = response.content.split(b"\0")[0]

    for i, chunk in enumerate(response.content.split(b"\0")):
        print(i, chunk.decode("utf-8"))

    # Checks that the first chunk is a valid ChatResponse object.
    try:
        message = ChatResponse.model_validate_json(first_response)
    except ValidationError as err:
        print(err)
        raise

    # Check that a chunk was cited
    assert message.context is not None, "A chunk should be cited."

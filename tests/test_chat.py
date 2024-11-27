from pydantic import ValidationError

from src.schemas.chat import ChatResponse, EventType


async def test_chat(client, parser):
    async with client.stream(
        "POST",
        "/chat",
        json={
            "page_slug": "page-26",
            "message": "Why should I write tests?",
        },
    ) as response:
        if response.is_error:
            await response.aread()
            try:
                error_detail = response.json().get("detail", "No detail provided")
            except ValueError:  # In case response isn't JSON
                error_detail = response.text
            print(f"{response.status_code} Error: {error_detail}")

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
        print("*" * 80)
        print("CHAT RESPONSE: ", parser(response))

    # Check that a chunk was cited
    assert message.context, "A chunk should be cited."


async def test_chat_CRI(client, parser):
    response = await client.post(
        "/chat/CRI",
        json={
            "page_slug": "page-26",
            "chunk_slug": "Test-Chunk-1718t",
            "student_response": "Predictions and goals.",
        },
    )
    assert response.status_code == 200, response.text
    print("*" * 80)
    print("CHAT CRI: ", parser(response.text))


async def test_user_guide_rag(client, parser):
    async with client.stream(
        "POST",
        "/chat",
        json={
            "page_slug": "page-26",
            "message": "How do I navigate the iTELL Dashboard?",
        },
    ) as response:
        if response.is_error:
            await response.aread()
            try:
                error_detail = response.json().get("detail", "No detail provided")
            except ValueError:  # In case response isn't JSON
                error_detail = response.text
            print(f"{response.status_code} Error: {error_detail}")

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
        print("*" * 80)
        print("CHAT USER GUIDE RAG:", parser(response))

    # Check that the first cited chunk is from the User Guide
    assert message.context[0] == "[User Guide]", "The user guide should be cited."


async def test_final_sert_response(client, parser):
    async with client.stream(
        "POST",
        "/chat/sert",
        json={
            "page_slug": "page-26",
            "current_chunk": "Test-Chunk-1718t",
            "message": "Yes",
            "history": [
                {
                    "text": "\n\nWhat is the relationship between the economic growth of a country and the strength of its legal framework, according",  # noqa: E501
                    "agent": "bot",
                },
                {
                    "text": "a strong legal framework, which ensures effective protection of property and contractual rights is crucial for economic growth. ",  # noqa: E501
                    "agent": "user",
                },
                {
                    "text": "\n\nThat's correct! According to the text, a strong legal framework that upholds property rights and contractual rights is essential for economic growth. It allows for effective transactions, contracts, and investments, which in turn promote economic growth. Can you think of any specific ways in which a weak legal framework might hinder economic growth?",  # noqa: E501
                    "agent": "bot",
                },
            ],
        },
    ) as response:
        if response.is_error:
            await response.aread()
            try:
                error_detail = response.json().get("detail", "No detail provided")
            except ValueError:  # In case response isn't JSON
                error_detail = response.text
            print(f"{response.status_code} Error: {error_detail}")

        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        # The first chunk is the feedback
        first_chunk = next(stream).removeprefix(f"event: {EventType.chat}\ndata: ")

        # Checks that the first chunk is a valid ChatResponse object.
        try:
            ChatResponse.model_validate_json(first_chunk)
        except ValidationError as err:
            print(err)
            raise
        print("*" * 80)
        print("FINAL SERT RESPONSE:", parser(response))

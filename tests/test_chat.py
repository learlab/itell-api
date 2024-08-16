from pydantic import ValidationError

from src.schemas.chat import ChatResponse, EventType


async def test_chat(client, parser):
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
        print("*" * 80)
        print("CHAT RESPONSE: ", parser(response))

    # Check that a chunk was cited
    assert len(message.context) != 0, "A chunk should be cited."


async def test_chat_CRI(client, parser):
    response = await client.post(
        "/chat/CRI",
        json={
            "page_slug": "emotional",
            "chunk_slug": "Core-Themes-3-483t",
            "student_response": "Predictions and goals.",
        },
    )
    assert response.status_code == 200
    print("*" * 80)
    print("CHAT CRI: ", parser(response.text))


async def test_user_guide_rag(client, parser):
    async with client.stream(
        "POST",
        "/chat",
        json={
            "page_slug": "emotional",
            "message": "How do I navigate the iTELL Dashboard?",
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
        print("*" * 80)
        print("CHAT USER GUIDE RAG:", parser(response))

    # Check that the first cited chunk is from the User Guide
    assert message.context[0] == "[User Guide]", "The user guide should be cited."


async def test_final_sert_response(client, parser):
    async with client.stream(
        "POST",
        "/chat/SERT",
        json={
            "page_slug": "7-1-the-relatively-recent-arrival-of-economic-growth",
            "current_chunk": "Rule-of-Law-and-Economic-Growth-701t",
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
        assert response.status_code == 200

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

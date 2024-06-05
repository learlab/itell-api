import json


async def test_chat_CRI(client):
    response = await client.post(
        "/chat/CRI",
        json={
            "page_slug": "emotional",
            "chunk_slug": "Core-Themes-3-483t",
            "student_response": "Predictions and goals.",
        },
    )
    assert response.status_code == 200

    try:
        print(
            json.loads([w for w in response.content.split(b"\x00") if w != b""][-1])[
                "text"
            ]
        )
    except Exception as e:
        print(e)

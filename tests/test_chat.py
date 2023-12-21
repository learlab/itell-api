import pytest
import os


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_chat(client):
    response = await client.post(
        "/chat",
        json={
            "page_slug": "what-is-law",
            "message": "What is the meaning of life?",
        },
    )
    assert response.status_code == 200

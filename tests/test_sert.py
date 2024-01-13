import pytest
import os


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_sert(client):
    response = await client.post(
        "/generate/sert",
        json={
            "page_slug": "a-sample-case",
            "summary": "What is the meaning of life?",
        },
    )
    assert response.status_code == 200
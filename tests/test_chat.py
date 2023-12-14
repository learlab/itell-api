def test_chat(client):
    response = client.post(
        "/chat",
        json={
            "page_slug": "what-is-law",
            "message": "What is the meaning of life?",
        },
    )
    assert response.status_code == 200
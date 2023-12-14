def test_short_answer(client):
    response = client.post(
        "/score/answer",
        json={
            "page_slug": "what-is-law",
            "chunk_slug": "Functions-of-the-Law-10t",
            "answer": "The natural rate of unemployment.",
        },
    )
    print("Short answer test results:", response.json())
    assert response.status_code == 200

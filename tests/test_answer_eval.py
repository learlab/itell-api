def test_short_answer_strapi(client):
    response = client.post(
        "/score/answer",
        json={
            "page_slug": "what-is-law",
            "chunk_slug": "Functions-of-the-Law-10t",
            "answer": "The natural rate of unemployment.",
        },
    )
    assert response.status_code == 200


def test_short_answer_missing_chunk_slug(client):
    response = client.post(
        "/score/answer",
        json={
            "page_slug": "what-is-law",
            "answer": "The natural rate of unemployment.",
        },
    )
    assert response.status_code == 422


def test_bad_slug(client):
    response = client.post(
        "/score/answer",
        json={
            "page_slug": "i-am-a-string-but-not-a-slug",
            "chunk_slug": "Functions-of-the-Law-10t",
            "answer": "The natural rate of unemployment.",
        },
    )
    assert response.status_code == 404

async def test_short_answer_strapi(client):
    response = await client.post(
        "/score/answer",
        json={
            "page_slug": "page-26",
            "chunk_slug": "Test-Chunk-1721t",
            "answer": "Writing tests helps to catch bugs early and serves as living documentation.",  # noqa: E501
        },
    )
    assert response.status_code == 200, response.text


async def test_short_answer_missing_chunk_slug(client):
    response = await client.post(
        "/score/answer",
        json={
            "page_slug": "page-26",
            "answer": "The natural rate of unemployment.",
        },
    )
    assert response.status_code == 422


async def test_bad_slug(client):
    response = await client.post(
        "/score/answer",
        json={
            "page_slug": "i-am-a-string-but-not-a-slug",
            "chunk_slug": "Functions-of-the-Law-10t",
            "answer": "The natural rate of unemployment.",
        },
    )
    assert response.status_code == 404

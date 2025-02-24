async def test_short_answer_strapi(client):
    response = await client.post(
        "/score/answer",
        json={
            "page_slug": "test-page",
            "chunk_slug": "Test-Chunk-1718t",
            "answer": "Writing tests helps to catch bugs early and serves as living documentation.",  # noqa: E501
        },
    )
    assert response.status_code == 200

async def test_short_answer_video_chunk(client):
    response = await client.post(
        "/score/answer",
        json={
            "page_slug": "test-page",
            "chunk_slug": "Test-Video-Chunk-50",
            "answer": "The principle of test-driven development called red green refactor involves writing a failing test first, then writing code to pass the test, and finally optimizing or refactoring the code.",  # noqa: E501
        },
    )
    assert response.status_code == 200, response.text

async def test_short_answer_missing_chunk_slug(client):
    response = await client.post(
        "/score/answer",
        json={
            "page_slug": "test-page",
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

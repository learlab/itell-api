async def test_summary_eval_strapi(client):
    response = await client.post(
        "/score/summary",
        json={
            "page_slug": "what-is-law",
            "summary": "Think about it this way: In 2015 the labor force in the United States contained over 158 million workers, according to the U.S. Bureau of Labor Statistics. The total land area was 3,794,101 square miles. While these are certainly large numbers, they are not infinite. Because these resources are limited, so are the numbers of goods and services we produce with them. Combine this with the fact that human wants seem to be virtually infinite, and you can see why scarcity is a problem.',",  # noqa: E501
        },
    )
    assert response.status_code == 200

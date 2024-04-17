import pytest
import os


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_summary_eval_stairs(client):
    """This test is not working with streaming. Currently using simple post test."""
    response = await client.post(
        "/score/summary/stairs",
        json={
            "page_slug": "emotional",
            "summary": "What is the meaning of life?",
        },
    )
    # print the first two chunks of the response
    for chunk in response.content.split(b"\0")[0:2]:
        print(chunk.decode())

    assert response.status_code == 200


# httpx.AsyncClient.stream() is not splitting the StreamingResponse for some reason.
# async def test_summary_eval_stairs(client):
#     async with client.stream(
#         "POST",
#         "/score/summary/stairs",
#         json={
#             "page_slug": "what-is-law",
#             "summary": (
#                 "Think about it this way: In 2015 the labor force in the United States"
#                 " contained over 158 million workers, according to the U.S. Bureau of"
#                 " Labor Statistics. The total land area was 3,794,101 square miles."
#                 " While these are certainly large numbers, they are not infinite."
#                 " Because these resources are limited, so are the numbers of goods and"
#                 " services we produce with them. Combine this with the fact that human"
#                 " wants seem to be virtually infinite, and you can see why scarcity is"
#                 " a problem.',"
#             ),
#         },
#     ) as response:
#         async for chunk in response.aiter_raw():
#             print(chunk.decode()[:50])
#             break

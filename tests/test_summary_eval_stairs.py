import pytest
import os
import json
import sys

from src.models import summary

@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_summary_eval_stairs_language(client):
    """This test is not working with streaming. Currently using simple post test."""
    response = await client.post(
        "/score/summary/stairs",
        json={
            "page_slug": "emotional",
            "summary": "Emotions are physical and mental states brought on by neurophysiological changes, variously associated with thoughts, feelings, behavioral responses, and a degree of pleasure or displeasure. There is no scientific consensus on a definition. Emotions are often intertwined with mood, temperament, personality, disposition, or creativity.",
        },
    )
    # combine and print the first two chunks of the response
    data = json.loads(response.content.split(b"\0")[0].decode())
    data.update(json.loads(response.content.split(b"\0")[1].decode()))

    # check that the status code is 200
    # throws assertion error if false
    assert response.status_code == 200

    # validate the response format
    # throws validation errors if false
    streaming_summary_results = summary.StreamingSummaryResults(**data)

    # check that the language score is passing
    # throws assertion error if false
    assert streaming_summary_results.prompt_details[7].type == 'Language', "Prompt details [7] should be Language."
    assert streaming_summary_results.prompt_details[7].feedback.is_passed == True, "Language score was too low."

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

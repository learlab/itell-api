import pytest
import os
from src.models.summary import SummaryResultsWithFeedback
from pydantic import ValidationError


async def test_summary_eval_stairs_language(client):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "emotional",
            "summary": "Emotions are physical and mental states brought on by neurophysiological changes, variously associated with thoughts, feelings, behavioral responses, and a degree of pleasure or displeasure. There is no scientific consensus on a definition. Emotions are often intertwined with mood, temperament, personality, disposition, or creativity.",  # noqa: E501
        },
    ) as response:
        assert response.status_code == 200

        # We need to simulate the streaming response due to an issue with
        # Starlette's TestClient https://github.com/encode/starlette/issues/1102
        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        # The first chunk is the feedback
        feedback = next(stream).removeprefix("event: summaryfeedback\ndata: ")

        # Checks that the feedback is a valid SummaryResultsWithFeedback object.
        try:
            feedback = SummaryResultsWithFeedback.model_validate_json(feedback)
        except ValidationError as err:
            print(err)
            raise

        # Check that the language score is passing
        language = next(
            item for item in feedback.prompt_details if item.type == "Language"
        )

        assert language.feedback.is_passed, "Language score should be passing."


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_bad_page_slug(client):
    response = await client.post(
        "/score/summary/stairs",
        json={
            "page_slug": "i-am-a-string-but-not-a-slug",
            "summary": "What is the meaning of life?",
        },
    )
    print(f"Response: {response.json()}")
    assert response.status_code == 404


@pytest.mark.skipif(os.getenv("ENV") == "development", reason="Requires GPU.")
async def test_empty_page(client):
    response = await client.post(
        "/score/summary/stairs",
        json={
            "page_slug": "test-page-no-chunks",
            "summary": "What is the meaning of life?",
        },
    )
    print(f"Response: {response.json()}")
    assert response.status_code == 404

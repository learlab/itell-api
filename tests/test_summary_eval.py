from pydantic import ValidationError

from src.schemas.summary import SummaryResultsWithFeedback


async def test_summary_eval_stairs(client):
    response = await client.post(
        "/score/summary",
        json={
            "page_slug": "emotional",
            "summary": "Emotions are physical and mental states brought on by neurophysiological changes, variously associated with thoughts, feelings, behavioral responses, and a degree of pleasure or displeasure. While there is no scientific consensus on a definition, emotions are often intertwined with mood, temperament, personality, disposition, or creativity.",  # noqa: E501
        },
    )

    assert response.status_code == 200

    feedback = SummaryResultsWithFeedback.model_validate(response.json())

    # Check that the content score is passing
    if feedback.metrics.content.is_passed is False:
        print(feedback.metrics.content.model_dump_json())
        raise AssertionError("Content score should be passing.")

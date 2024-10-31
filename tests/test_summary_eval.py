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

    # Check that the language score is passing
    language = next(
        item for item in feedback.prompt_details if item.type == "Language"
    )

    if not language.feedback.is_passed:
        print(feedback.model_dump_json())
        raise AssertionError("Language score should be passing.")
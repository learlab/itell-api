from src.schemas.summary import SummaryResultsWithFeedback


async def test_summary_eval(client):
    response = await client.post(
        "/score/summary",
        json={
            "page_slug": "page-26",
            "summary": "Writing tests is essential in software development. They catch bugs early, serve as reliable documentation, and give developers confidence to improve code without introducing errors. Testing also promotes better code design through modular architecture and clear interfaces. The investment in writing tests pays off through more maintainable, reliable software.",  # noqa: E501
        },
    )

    assert response.status_code == 200, response.text

    feedback = SummaryResultsWithFeedback.model_validate(response.json())

    # Check that the content score is passing
    if feedback.metrics.content.is_passed is False:
        print(feedback.metrics.content.model_dump_json())
        raise AssertionError("Content score should be passing.")

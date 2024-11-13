from pydantic import ValidationError

from src.schemas.chat import EventType
from src.schemas.summary import SummaryResultsWithFeedback

import tomllib


async def test_summary_eval_stairs(client, supabase):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "emotional",
            "summary": "Emotions are physical and mental states brought on by neurophysiological changes, variously associated with thoughts, feelings, behavioral responses, and a degree of pleasure or displeasure. While there is no scientific consensus on a definition, emotions are often intertwined with mood, temperament, personality, disposition, or creativity.",  # noqa: E501
        },
    ) as response:
        assert response.status_code == 200

        # We need to simulate the streaming response due to an issue with
        # Starlette's TestClient https://github.com/encode/starlette/issues/1102
        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        # The first chunk is the feedback
        feedback = next(stream).removeprefix(
            f"event: {EventType.summary_feedback}\ndata: "
        )

        # Checks that the feedback is a valid SummaryResultsWithFeedback object.
        try:
            feedback = SummaryResultsWithFeedback.model_validate_json(feedback)
        except ValidationError as err:
            print(err)
            raise

        # Check that the content score is passing
        if not feedback.metrics.content.is_passed:
            print(feedback.metrics.content.model_dump_json())
            raise AssertionError("Content score should be passing.")

        supabase.reset_volume_prior("cornell")


async def test_summary_eval_stairs_fail_content(client, parser, supabase):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "learning-analytics-for-self-regulated-learning",
            "summary": "The paper introcuces what is self-regulated learning is, and elabrates the more granular definition of each faucets. COPES are a good words to memorize the concept, but overally spearking these terms are still pretty abstract for me. Collecting is hard, but it seems like collecting right data and utlize it is way more critical. ",  # noqa: E501
        },
    ) as response:
        assert response.status_code == 200

        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        feedback = next(stream).removeprefix(
            f"event: {EventType.summary_feedback}\ndata: "
        )
        feedback = SummaryResultsWithFeedback.model_validate_json(feedback)

        # Check that the Content score is failing
        if feedback.metrics.content.is_passed:
            print(feedback.metrics.content.model_dump_json())
            raise AssertionError("Content score should be failing.")
        print("*" * 80)
        print("SERT QUESTION: ", parser(response))

        await supabase.reset_volume_prior("cornell")


async def test_threshold_adjustment(client, supabase):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "learning-analytics-for-self-regulated-learning",
            "summary": "The paper introcuces what is self-regulated learning is, and elabrates the more granular definition of each faucets. COPES are a good words to memorize the concept, but overally spearking these terms are still pretty abstract for me. Collecting is hard, but it seems like collecting right data and utlize it is way more critical. ",  # noqa: E501
            "score_history": [1.5, 1.5, 1.9, 2.0, 3.5],
        },
    ) as response:
        assert response.status_code == 200

        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        feedback = next(stream).removeprefix(
            f"event: {EventType.summary_feedback}\ndata: "
        )
        feedback = SummaryResultsWithFeedback.model_validate_json(feedback)

        # Check that the Content threshold was adjusted upwards
        assert (
            feedback.metrics.content.threshold > 0.07
        ), "Threshold should have been adjusted upwards."

        with open("assets/global_prior.toml", "rb") as f:
            global_prior = tomllib.load(f)

        await supabase.reset_volume_prior("cornell")
        reset_prior = await supabase.get_volume_prior("cornell")
        assert (
            reset_prior.mean == global_prior["mean"]
        ), "Prior mean should have been reset to 0.2."


async def test_bad_page_slug(client):
    response = await client.post(
        "/score/summary/stairs",
        json={
            "page_slug": "i-am-a-string-but-not-a-slug",
            "summary": "What is the meaning of life?",
        },
    )
    assert response.status_code == 404


async def test_empty_page(client):
    response = await client.post(
        "/score/summary/stairs",
        json={
            "page_slug": "test-page-no-chunks",
            "summary": "What is the meaning of life?",
        },
    )
    assert response.status_code == 404

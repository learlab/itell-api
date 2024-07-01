from pydantic import ValidationError
from src.models.chat import EventType
from src.models.summary import SummaryResultsWithFeedback


async def test_summary_eval_stairs(client, parser):
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

        # Check that the language score is passing
        language = next(
            item for item in feedback.prompt_details if item.type == "Language"
        )

        if not language.feedback.is_passed:
            print(feedback.model_dump_json())
            raise AssertionError("Language score should be passing.")


async def test_summary_eval_stairs_fail_language(client, parser):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "emotional",
            "summary": "Before this, all my low-effort summaries just reiterated keywords from the title. This time, I'll throw in some keyphrases from the passage. This page discusses how we can detect affect from student activity and bodily signals. Some themes that are relevant to the analysis of such affect data are classroom analysis, teacher analysis, and sentiment analysis. Overall, it's all about measuring and analyzing students' emotions.",  # noqa: E501
        },
    ) as response:
        assert response.status_code == 200

        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        feedback = next(stream).removeprefix(
            f"event: {EventType.summary_feedback}\ndata: "
        )
        feedback = SummaryResultsWithFeedback.model_validate_json(feedback)

        # Check that the language score is failing
        language = next(
            item for item in feedback.prompt_details if item.type == "Language"
        )

        if language.feedback.is_passed:
            print(feedback.model_dump_json())
            raise AssertionError("Language score should be failing.")
        print("*" * 80)
        print("LANGUAGE FEEDBACK: ", parser(response))


async def test_summary_eval_stairs_fail_content(client, parser):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "learning-an-1",
            "summary": "Choosing the correct visualization to use for a dataset is essential in making sure researchers can answer the questions they have about the data and are working to answer, especially as there are many alternatives that can be considered. Additionally, even after visualizations are made, it is important to evaluate them to make sure the effectiveness, efficiency, and usefulness is known.",  # noqa: E501
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
        content = next(
            item for item in feedback.prompt_details if item.type == "Content"
        )

        if content.feedback.is_passed:
            print(feedback.model_dump_json())
            raise AssertionError("Content score should be failing.")
        print("*" * 80)
        print("SERT QUESTION: ", parser(response))


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

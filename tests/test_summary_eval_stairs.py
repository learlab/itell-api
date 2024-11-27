from pydantic import ValidationError

from src.schemas.chat import EventType
from src.schemas.summary import SummaryResultsWithFeedback


async def test_summary_eval_stairs(client, supabase):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "page-26",
            "summary": "Writing tests is essential in software development. They catch bugs early, serve as reliable documentation, and give developers confidence to improve code without introducing errors. Testing also promotes better code design through modular architecture and clear interfaces. The investment in writing tests pays off through more maintainable, reliable software.",  # noqa: E501
        },
    ) as response:
        if response.is_error:
            await response.aread()
            try:
                error_detail = response.json().get("detail", "No detail provided")
            except ValueError:  # In case response isn't JSON
                error_detail = response.text
            print(f"{response.status_code} Error: {error_detail}")

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
            "page_slug": "page-26",
            "summary": "Tests r rly important 4 making software!!!! They help u find bugs b4 they get 2 bad LOL!! When u write tests its like having a safety blanket 4 ur code. Tests r gr8 documentation 2!! U can change stuff without breaking everything else. Tests make code way better OMG!!!!!! Developers luv them!!",  # noqa: E501
        },
    ) as response:
        if response.is_error:
            await response.aread()
            try:
                error_detail = response.json().get("detail", "No detail provided")
            except ValueError:  # In case response isn't JSON
                error_detail = response.text
            print(f"{response.status_code} Error: {error_detail}")

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
            "page_slug": "page-27",
            "summary": "What is the meaning of life?",
        },
    )
    assert response.status_code == 404

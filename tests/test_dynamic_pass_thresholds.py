import tomllib

from src.pipelines.conjugate_normal import ConjugateNormal
from src.schemas.chat import EventType
from src.schemas.prior import VolumePrior
from src.schemas.summary import SummaryResultsWithFeedback

with open("assets/global_prior.toml", "rb") as f:
    global_prior = VolumePrior(slug="global", **tomllib.load(f))


async def test_threshold_adjustment(client, supabase):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            "page_slug": "test-page",
            "summary": "Writing tests is essential in software development. They catch bugs early, serve as reliable documentation, and give developers confidence to improve code without introducing errors. Testing also promotes better code design through modular architecture and clear interfaces. The investment in writing tests pays off through more maintainable, reliable software.",  # noqa: E501
            "score_history": [1.5, 1.5, 1.9, 2.0, 3.5],
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

        # Check that the Content threshold was adjusted upwards
        assert (
            feedback.metrics.content.threshold > 0.07
        ), "Threshold should have been adjusted upwards."

        await supabase.reset_volume_prior("test-volume")
        reset_prior = await supabase.get_volume_prior("test-volume")
        assert (
            reset_prior.mean == global_prior.mean
        ), "Prior mean should have been reset to 0.2."


async def test_new_volume_threshold(client, supabase):
    async with client.stream(
        "POST",
        "/score/summary/stairs",
        json={
            # Use the User Guide because it will exist in Strapi,
            # but we can safely delete the volume threshold after it is created.
            "page_slug": "test-page",
            "summary": "Writing tests is essential in software development. They catch bugs early and give developers shame about their inability to accomplish the most basic tasks. While reliable software is ostensibly the goal, the true value of tests is that they weed out feeble-minded tech bros from the profession.",  # noqa: E501
            "score_history": [],
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

        # Check that the Content threshold is set to the global prior
        global_threshold = ConjugateNormal(global_prior).threshold
        assert round(feedback.metrics.content.threshold, 2) == round(
            global_threshold, 2
        ), f"Threshold should be set to {global_threshold}."

        # Delete the volume prior for "user-guide"
        await supabase.delete_volume_prior("test-volume")
        empty_response = (
            await supabase.table("volume_priors")
            .select("*")
            .eq("slug", "test-volume")
            .execute()
        )

        assert (
            not empty_response.data
        ), 'Volume prior for "test-volume" should have been deleted.'

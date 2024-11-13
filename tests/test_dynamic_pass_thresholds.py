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

        await supabase.reset_volume_prior("cornell")
        reset_prior = await supabase.get_volume_prior("cornell")
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
            "page_slug": "user-guide-baseline",
            "summary": "iTELL is a learning tool that is designed to help students ingest reading materials effectively. Reading in iTELL is complemented by activities such as short answer questions and end-of-page summaries. These activities are required in order to proceed with the reading, and they are evaluated by AI. Learners may also use the Guide-on-the-side to converse about their reading, and they can see performance metrics in the user dashboard.",  # noqa: E501
            "score_history": [],
        },
    ) as response:
        assert response.status_code == 200

        response = await anext(response.aiter_text())
        stream = (chunk for chunk in response.split("\n\n"))

        feedback = next(stream).removeprefix(
            f"event: {EventType.summary_feedback}\ndata: "
        )

        feedback = SummaryResultsWithFeedback.model_validate_json(feedback)

        # Check that the Content threshold is set to the global prior
        global_threshold = ConjugateNormal(global_prior).threshold
        assert round(feedback.metrics.content.threshold, 3) == round(
            global_threshold, 3
        ), f"Threshold should be set to {global_threshold}."

        # Delete the volume prior for "user-guide"
        await supabase.delete_volume_prior("user-guide")
        empty_response = (
            await supabase.table("volume_priors")
            .select("*")
            .eq("slug", "user-guide")
            .execute()
        )

        assert (
            not empty_response.data
        ), 'Volume prior for "user-guide" should have been deleted.'

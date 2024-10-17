import tomllib

from ..pipelines.feedback_processor import FeedbackProcessor
from ..schemas.summary import (
    AnalyticFeedback,
    SummaryResults,
    SummaryResultsWithFeedback,
)

feedback_processors = {}
with open("assets/summary_feedback.toml", "rb") as f:
    feedback_config = tomllib.load(f)
    for score_type, values in feedback_config.items():
        feedback_processors[score_type] = FeedbackProcessor(**values)


def summary_feedback(results: SummaryResults) -> SummaryResultsWithFeedback:
    """Provide feedback on a summary based on the results
    of the summary scoring model."""

    prompt_details: list[AnalyticFeedback] = [
        feedback_processors["containment"](results.containment),
        feedback_processors["containment_chat"](results.containment_chat),
        feedback_processors["similarity"](results.similarity),
        feedback_processors["content"](
            results.content, threshold=results.content_threshold
        ),
        feedback_processors["english"](results.english),
        feedback_processors["profanity"](results.profanity),
        feedback_processors["language"](results.language),
    ]

    # Overall Feedback
    # Check if all feedback that exists is passing
    # Ignores feedback with .is_passed = None
    is_passed: bool = all(
        feedback.feedback.is_passed is not False for feedback in prompt_details
    )

    if is_passed:
        prompt = (
            "Excellent job summarizing the text. Please move forward to the next page."
        )
    else:
        prompt = (
            "Before moving onto the next page, you will need to revise the summary you"
            " wrote using the feedback provided."
        )

    return SummaryResultsWithFeedback(
        **results.model_dump(),
        is_passed=is_passed,
        prompt=prompt,
        prompt_details=prompt_details,
    )

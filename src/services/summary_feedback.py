import tomllib

from ..pipelines.feedback_processor import FeedbackProcessor
from ..schemas.summary import (
    SummaryMetrics,
    _SummaryResults,
    SummaryResultsWithFeedback,
)

feedback_processors = {}
with open("assets/summary_feedback.toml", "rb") as f:
    feedback_config = tomllib.load(f)
    for score_type, values in feedback_config.items():
        feedback_processors[score_type] = FeedbackProcessor(**values)


def summary_feedback(results: _SummaryResults) -> SummaryResultsWithFeedback:
    """Provide feedback on a summary based on the results
    of the summary scoring model."""

    metrics = SummaryMetrics(
        containment=feedback_processors["containment"](results.containment),
        containment_chat=feedback_processors["containment_chat"](
            results.containment_chat
        ),
        similarity=feedback_processors["similarity"](results.similarity),
        content=feedback_processors["content"](
            results.content, threshold=results.content_threshold
        ),
        english=feedback_processors["english"](results.english),
        profanity=feedback_processors["profanity"](results.profanity),
    )

    # Overall Feedback
    # Check if all feedback that exists is passing
    # Ignores feedback with .is_passed = None
    is_passed: bool = all(
        feedback["is_passed"] is not False for feedback in metrics.model_dump().values()
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
        is_passed=is_passed,
        prompt=prompt,
        metrics=metrics,
    )

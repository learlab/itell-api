from .models.summary import (
    ScoreType,
    Feedback,
    AnalyticFeedback,
    SummaryResults,
    SummaryResultsWithFeedback,
)

from typing import Union

feedback_dict = {
    "containment": {
        "threshold": 0.6,
        "passing": (
            "You did a good job of using your own language to describe the main ideas"
            " of the text."
        ),
        "failing": (
            "You need to rely less on the language in the text and focus more on"
            " rewriting the key ideas."
        ),
    },
    "containment_chat": {
        "threshold": 0.6,
        "passing": (
            "You did a good job of using your own language to describe the main ideas"
            " of the text."
        ),
        "failing": "You need to depend less on the examples provided by iTELL AI.",
    },
    "similarity": {
        "threshold": 0.5,
        "passing": (
            "You did a good job of staying on topic and writing about the main ideas of"
            " the text."
        ),
        "failing": (
            "To be successful, you need to stay on topic. Find the main ideas of"
            " the text and focus your summary on those ideas."
        ),
    },
    "content": {
        "threshold": -0.5,
        "passing": (
            "You did a good job of including key ideas and details on this page."
        ),
        "failing": (
            "You need to include more key ideas and details from the page to"
            " successfully summarize the content. Consider focusing on the main ideas"
            " of the text and providing support for those ideas in your summary."
        ),
    },
    "wording": {
        "threshold": -1,
        "passing": (
            "You did a good job of paraphrasing words and sentences from the text and"
            " using objective language."
        ),
        "failing": (
            "You need to paraphrase words and ideas on this page better. Focus on using"
            " different words and sentences than those used in the text. Also, try to"
            " use more objective language (or less emotional language)."
        ),
    },
    "english": {
        "threshold": False,
        "passing": None,
        "failing": "Please write your summary in English.",
    },
}


def analytic_feedback(
    score: Union[float, None], score_type: ScoreType
) -> AnalyticFeedback:
    score_feedback = feedback_dict[score_type.name]
    if score is None:
        feedback = Feedback(is_passed=False, prompt=None)
    elif score <= score_feedback["threshold"]:
        feedback = Feedback(is_passed=False, prompt=score_feedback["failing"])
    else:
        feedback = Feedback(is_passed=True, prompt=score_feedback["passing"])

    return AnalyticFeedback(type=score_type, feedback=feedback)


def get_feedback(summary_results: SummaryResults) -> SummaryResultsWithFeedback:
    containment = analytic_feedback(summary_results.containment, ScoreType.containment)
    containment_chat = analytic_feedback(
        summary_results.containment_chat, ScoreType.containment_chat
    )
    similarity = analytic_feedback(summary_results.similarity, ScoreType.similarity)
    english = analytic_feedback(summary_results.english, ScoreType.english)
    content = analytic_feedback(summary_results.content, ScoreType.content)
    wording = analytic_feedback(summary_results.wording, ScoreType.wording)

    is_passed = all(
        feedback.feedback.is_passed
        for feedback in [
            containment,
            containment_chat,
            similarity,
            english,
            wording,
            content,
        ]
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
        **summary_results.dict(),
        is_passed=is_passed,
        prompt=prompt,
        prompt_details=[
            containment,
            containment_chat,
            similarity,
            english,
            content,
            wording,
        ],
    )

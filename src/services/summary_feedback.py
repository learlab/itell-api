import math
import operator
from typing import Callable, Literal
from ..schemas.summary import (
    AnalyticFeedback,
    Feedback,
    ScoreType,
    SummaryResults,
    SummaryResultsWithFeedback,
)


class FeedbackProcessor:
    def __init__(
        self,
        score_type: ScoreType,
        threshold: float,
        comparator: Callable[[float, float], bool],
        feedback: list[str],
        feedback_indexer: Literal["floor"] = None,
    ):
        self.score_type = score_type
        self.threshold = threshold
        self.comparator = comparator
        self.feedback = feedback
        if feedback_indexer == "floor":
            self.feedback_indexer = self.floor_indexer
        else:
            self.feedback_indexer = self.default_indexer

    def default_indexer(self, score: float) -> Literal[0, 1]:
        """Returns 0 is score is failing, 1 if score is passing."""
        return 0 if self.comparator(score, self.threshold) else 1

    def floor_indexer(self, score: float) -> int:
        """Returns the floor of the score."""
        return math.floor(score)

    def __call__(self, score: float):
        if score is None:
            feedback = Feedback(is_passed=None, prompt=None)
        else:
            is_passed = self.comparator(score, self.threshold)
            prompt = self.feedback[self.feedback_indexer(score)]
            feedback = Feedback(is_passed=is_passed, prompt=prompt)
        return AnalyticFeedback(type=self.score_type, feedback=feedback)


containment = FeedbackProcessor(
    score_type=ScoreType.containment,
    threshold=0.6,
    comparator=operator.lt,
    feedback=[
        "You need to rely less on the language in the text and focus more on rewriting the key ideas.",  # noqa: E501
        "You did a good job of using your own language to describe the main ideas of the text.",  # noqa: E501
    ],
)

containment_chat = FeedbackProcessor(
    score_type=ScoreType.containment_chat,
    threshold=0.6,
    comparator=operator.lt,
    feedback=[
        "You need to depend less on the examples provided by iTELL AI.",
        "You did a good job of using your own language to describe the main ideas of the text.",  # noqa: E501
    ],
)

similarity = FeedbackProcessor(
    score_type=ScoreType.similarity,
    threshold=0.5,
    comparator=operator.gt,
    feedback=[
        "To be successful, you need to stay on topic. Find the main ideas of the text and focus your summary on those ideas.",  # noqa: E501
        "You did a good job of staying on topic and writing about the main ideas of the text.",  # noqa: E501
    ],
)

content = FeedbackProcessor(
    score_type=ScoreType.content,
    threshold=0,  # 0 for Prolific testing
    comparator=operator.gt,
    feedback=[
        "You need to include more key ideas and details from the page to successfully summarize the content. Consider focusing on the main ideas of the text and providing support for those ideas in your summary.",  # noqa: E501
        "You did a good job of including key ideas and details on this page.",
    ],
)

language = FeedbackProcessor(
    score_type=ScoreType.language,
    threshold=2.0,  # 2.0 for Prolific testing
    comparator=operator.gt,
    feedback=[
        "Your summary shows a very basic understanding of lexical and syntactic structures.",  # noqa: E501
        "Your summary shows an understanding of lexical and syntactic structures.",
        "Your summary shows an appropriate range of lexical and syntactic structures.",
        "Your summary shows an excellent range of lexical and syntactic structures.",
        "Your summary shows an excellent range of lexical and syntactic structures.",
    ],
)

english = FeedbackProcessor(
    score_type=ScoreType.english,
    threshold=False,
    comparator=operator.gt,
    feedback=["Please write your summary in English.", None],
)

profanity = FeedbackProcessor(
    score_type=ScoreType.profanity,
    threshold=True,
    comparator=operator.lt,
    feedback=["Please avoid using profanity in your summary.", None],
)


def summary_feedback(results: SummaryResults) -> SummaryResultsWithFeedback:
    prompt_details = [
        containment(results.containment),
        containment_chat(results.containment_chat),
        similarity(results.similarity),
        content(results.content),
        english(results.english),
        profanity(results.profanity),
        language(results.language),
    ]

    is_passed = all(feedback.feedback.is_passed for feedback in prompt_details)

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

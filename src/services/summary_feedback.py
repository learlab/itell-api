import math
import operator
from typing import Callable, Literal, Union

from ..schemas.summary import (
    AnalyticFeedback,
    Feedback,
    ScoreType,
    SummaryResults,
    SummaryResultsWithFeedback,
)


class FeedbackProcessor:
    """A generic class for calculating feedback.
    Initialized with a comparator function, a passing threshold,
    and a list of feedback strings.

    The comparator callable is used by the __call__ method and should accept the score
    as the first argument and the threshold as the second argument.
    It should return True when the score is passing and False when the score is failing.
    Example: operator.gt(score, threshold) returns True when score > threshold.

    Feedback_indexers determine how the score (and threshold) should be translated
    into an int that is used to index the appropriate feedback string.
    """

    def __init__(
        self,
        score_type: ScoreType,
        threshold: float | bool,
        comparator: Callable[[any, any], bool],
        feedback: list[str],
        feedback_indexer: Literal["default", "floor"] = "default",
    ):
        self.score_type = score_type
        self.threshold = threshold
        self.comparator = comparator
        self.feedback = feedback
        if feedback_indexer == "default":
            self.feedback_indexer = self._default_indexer
        elif feedback_indexer == "floor":
            self.feedback_indexer = self._floor_indexer

    def _default_indexer(self, score: float) -> Literal[0, 1]:
        """Returns 0 is score is passing, 1 if score is failing."""
        return 0 if self.comparator(score, self.threshold) else 1

    def _floor_indexer(self, score: float) -> int:
        """Returns the floor of the score."""
        return math.floor(score)

    def __call__(self, score: Union[float, bool, None]) -> AnalyticFeedback:
        if score is None:
            feedback = Feedback(is_passed=None, prompt=None)
        else:
            is_passed = self.comparator(score, self.threshold)
            prompt = self.feedback[self.feedback_indexer(score)]
            feedback = Feedback(is_passed=is_passed, prompt=prompt)
        return AnalyticFeedback(type=self.score_type, feedback=feedback)


# Passing summaries have less than threshold containment score
containment = FeedbackProcessor(
    score_type=ScoreType.containment,
    threshold=0.6,
    comparator=operator.lt,
    feedback=[
        "You did a good job of using your own language to describe the main ideas of the text.",  # noqa: E501
        "You need to rely less on the language in the text and focus more on rewriting the key ideas.",  # noqa: E501
    ],
)

# Passing summaries have less than threshold containment score
containment_chat = FeedbackProcessor(
    score_type=ScoreType.containment_chat,
    threshold=0.6,
    comparator=operator.lt,
    feedback=[
        "You did a good job of using your own language to describe the main ideas of the text.",  # noqa: E501
        "You need to depend less on the examples provided by iTELL AI.",
    ],
)

similarity = FeedbackProcessor(
    score_type=ScoreType.similarity,
    threshold=0.5,
    comparator=operator.gt,
    feedback=[
        "You did a good job of staying on topic and writing about the main ideas of the text.",  # noqa: E501
        "To be successful, you need to stay on topic. Find the main ideas of the text and focus your summary on those ideas.",  # noqa: E501
    ],
)

content = FeedbackProcessor(
    score_type=ScoreType.content,
    threshold=0,  # 0 for Prolific testing
    comparator=operator.gt,
    feedback=[
        "You did a good job of including key ideas and details on this page.",
        "You need to include more key ideas and details from the page to successfully summarize the content. Consider focusing on the main ideas of the text and providing support for those ideas in your summary.",  # noqa: E501
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

# Passing summaries have > False English score (English is detected)
english = FeedbackProcessor(
    score_type=ScoreType.english,
    comparator=operator.gt,
    threshold=False,
    feedback=[
        None,  # No feedback for passing
        "Please write your summary in English.",
    ],
)

# Passing summaries have < True profanity score (Profanity is not detected)
profanity = FeedbackProcessor(
    score_type=ScoreType.profanity,
    comparator=operator.lt,
    threshold=True,
    feedback=[
        None,  # No feedback for passing
        "Please avoid using profanity in your summary.",
    ],
)


def summary_feedback(results: SummaryResults) -> SummaryResultsWithFeedback:
    """Provide feedback on a summary based on the results
    of the summary scoring model."""
    prompt_details: list[AnalyticFeedback] = [
        containment(results.containment),
        containment_chat(results.containment_chat),
        similarity(results.similarity),
        content(results.content),
        english(results.english),
        profanity(results.profanity),
        language(results.language),
    ]

    # Overall Feedback
    # Check if all feedback that exists is passing
    # Ignores feedback with .is_passed = None
    is_passed: bool = all(
        feedback.feedback.is_passed
        for feedback in prompt_details
        if feedback.feedback.is_passed is not None
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

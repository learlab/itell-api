import math
import operator
from typing import Literal

from ..schemas.summary import AnalyticFeedback, ScoreType


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

    op_dict = {"gt": operator.gt, "lt": operator.lt, "eq": operator.eq}

    def __init__(
        self,
        score_type: ScoreType,
        threshold: float | bool,
        comparator: Literal["gt", "lt", "eq"],
        feedback: list[str],
    ):
        self.score_type = score_type
        self.threshold = threshold
        self.comparator = self.op_dict[comparator]
        self.feedback = feedback
        if len(feedback) > 2:
            # If there are more than 2 feedback strings, use the floor indexer
            self.feedback_indexer = self._floor_indexer
        else:
            self.feedback_indexer = self._default_indexer

    def _default_indexer(
        self, score: float, threshold: float | bool = None
    ) -> Literal[0, 1]:
        """Returns 1 if score is passing, 0 if score is failing."""

        return int(self.comparator(score, threshold))

    def _floor_indexer(self, score: float) -> int:
        """Returns the floor of the score."""
        return math.floor(score)

    def __call__(
        self,
        score: float | bool | None,
        threshold: float | bool | None = None,
    ) -> AnalyticFeedback:

        if threshold is None:
            threshold = self.threshold

        if score is None:
            return AnalyticFeedback(
                name=self.score_type,
                threshold=threshold,
            )

        else:
            return AnalyticFeedback(
                name=self.score_type,
                is_passed=self.comparator(score, threshold),
                score=score,
                threshold=threshold,
                feedback=self.feedback[self.feedback_indexer(score, threshold)],
            )

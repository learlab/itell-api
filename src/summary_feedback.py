from .models.summary import (
    ScoreType,
    Feedback,
    AnalyticFeedback,
    SummaryResults,
    SummaryResultsWithFeedback,
)


class Originality:
    threshold = 0.6
    passing = (
        "You did a good job of using your own language to describe the main ideas"
        " of the text."
    )
    failing = (
        "You need to rely less on the language in the text and focus more on"
        " rewriting the key ideas."
    )

    @classmethod
    def generate_feedback(cls, score):
        is_passed = score < cls.threshold
        feedback = Feedback(
            is_passed=is_passed, prompt=cls.passing if is_passed else cls.failing
        )
        return AnalyticFeedback(type=ScoreType.originality, feedback=feedback)


class OriginalityChat:
    threshold = 0.6
    passing = (
        "You did a good job of using your own language to describe the main ideas"
        " of the text."
    )
    failing = "You need to depend less on the examples provided by iTELL AI."

    @classmethod
    def generate_feedback(cls, score):
        if score is None:
            feedback = Feedback(is_passed=None, prompt=None)
        else:
            is_passed = score < cls.threshold
            feedback = Feedback(
                is_passed=is_passed, prompt=cls.passing if is_passed else cls.failing
            )
        return AnalyticFeedback(type=ScoreType.originality_chat, feedback=feedback)


class Relevance:
    threshold = 0.5
    passing = (
        "You did a good job of staying on topic and writing about the main ideas of"
        " the text."
    )
    failing = (
        "To be successful, you need to stay on topic. Find the main ideas of"
        " the text and focus your summary on those ideas."
    )

    @classmethod
    def generate_feedback(cls, score):
        is_passed = score > cls.threshold
        feedback = Feedback(
            is_passed=is_passed, prompt=cls.passing if is_passed else cls.failing
        )
        return AnalyticFeedback(type=ScoreType.relevance, feedback=feedback)


class Content:
    threshold = -0.5
    passing = "You did a good job of including key ideas and details on this page."
    failing = (
        "You need to include more key ideas and details from the page to"
        " successfully summarize the content. Consider focusing on the main ideas"
        " of the text and providing support for those ideas in your summary."
    )

    @classmethod
    def generate_feedback(cls, score):
        if score is None:
            feedback = Feedback(is_passed=None, prompt=None)
        else:
            is_passed = score > cls.threshold
            feedback = Feedback(
                is_passed=is_passed, prompt=cls.passing if is_passed else cls.failing
            )
        return AnalyticFeedback(type=ScoreType.content, feedback=feedback)


class Wording:
    threshold = -1
    passing = (
        "You did a good job of paraphrasing words and sentences from the text and"
        " using objective language."
    )
    failing = (
        "You need to paraphrase words and ideas on this page better. Focus on using"
        " different words and sentences than those used in the text. Also, try to"
        " use more objective language (or less emotional language)."
    )

    @classmethod
    def generate_feedback(cls, score):
        if score is None:
            feedback = Feedback(is_passed=None, prompt=None)
        else:
            is_passed = score > cls.threshold
            feedback = Feedback(
                is_passed=is_passed, prompt=cls.passing if is_passed else cls.failing
            )
        return AnalyticFeedback(type=ScoreType.wording, feedback=feedback)


class English:
    threshold = False
    passing = None
    failing = "Please write your summary in English."

    @classmethod
    def generate_feedback(cls, score):
        is_passed = score > cls.threshold
        feedback = Feedback(
            is_passed=is_passed, prompt=cls.passing if is_passed else cls.failing
        )
        return AnalyticFeedback(type=ScoreType.english, feedback=feedback)


def get_feedback(results: SummaryResults) -> SummaryResultsWithFeedback:
    originality = Originality.generate_feedback(results.originality)
    originality_chat = OriginalityChat.generate_feedback(results.originality_chat)
    relevance = Relevance.generate_feedback(results.relevance)
    content = Content.generate_feedback(results.content)
    wording = Wording.generate_feedback(results.wording)
    english = English.generate_feedback(results.english)

    is_passed = all(
        feedback.feedback.is_passed is not False
        for feedback in [
            originality,
            originality_chat,
            relevance,
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
        **results.dict(),
        is_passed=is_passed,
        prompt=prompt,
        prompt_details=[
            originality,
            originality_chat,
            relevance,
            english,
            content,
            wording,
        ],
    )

from models.answer import AnswerInput, AnswerResults
import random


class Answer:
    threshold = 0.5  # Minimum score to be considered correct

    def __init__(self, answer_input: AnswerInput):
        self.chapter_index = answer_input.chapter_index
        self.section_index = answer_input.section_index
        self.subsection_index = answer_input.subsection_index
        self.section_index = f"{self.chapter_index:02}-{self.section_index:02}"
        self.subsection_index = (
            f"{self.section_index}"
            "-"
            f"-{self.subsection_index:02}"
        )

        self.answer = answer_input.answer
        self.results = {}

    def score_answer(self) -> None:
        """Placeholder for BLEURT model implementation.
        Currently adds random float (between -1 and 1 to mimic BEURT)
        and random bool to result dict"""

        """

        INSERT CODE FOR BLEURT MODEL
        replace random values below with actual scores

        """

        score = random.uniform(-1, 1)

        self.results["score"] = score
        self.results["is_passing"] = bool(score > self.threshold)


def answer_score(answer_input: AnswerInput) -> AnswerResults:
    answer = Answer(answer_input)
    answer.score_answer()

    return AnswerResults(**answer.results)

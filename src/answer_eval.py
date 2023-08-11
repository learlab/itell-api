from models.answer import AnswerInput, AnswerResults
from supabase import Client
import random


class Answer:
    threshold = 0.5  # Minimum score to be considered correct

    def __init__(self, answer_input: AnswerInput, db: Client):
        section_index = (
            f"{answer_input.chapter_index:02}-{answer_input.section_index:02}"
        )

        self.data = (
            db.table("subsections")
            .select("clean_text", "question", "answer")
            .eq("section_id", section_index)
            .eq("subsection", answer_input.subsection_index)
            .execute()
            .data
        )

        self.answer = answer_input.answer
        self.results = {}

    def score_answer(self) -> None:
        """Placeholder for BLEURT model implementation.
        Currently adds random float (between -1 and 1 to mimic BEURT)
        and random bool to result dict"""

        """

        TODO: INSERT CODE FOR BLEURT MODEL
        replace random values below with actual scores

        """

        score = random.uniform(-1, 1)

        self.results["score"] = score
        self.results["is_passing"] = bool(score > self.threshold)


def answer_score(answer_input: AnswerInput) -> AnswerResults:
    from database import db

    answer = Answer(answer_input, db)
    answer.score_answer()

    return AnswerResults(**answer.results)

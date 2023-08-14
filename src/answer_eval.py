from models.answer import AnswerInput, AnswerResults
from supabase import Client
from bleurt import score as score_lib
import random
from pathlib import Path


class Answer:
    # NOTE: The optimal threhsold basis the chatgpt/vicuna dataset is 0.6 for this BLEURT model.
    threshold = 0.6  # Minimum score to be considered correct
    
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

        self.batch_size = 16
        self.bleurt_scorer = score_lib.BleurtScorer(str(Path("assets/bleurt")))
    
    def score_answer(self) -> None:
        """
        The function uses finetuned BLEURT model to score input answers.
        """

        score = self.bleurt_scorer.score(references=[self.data[0]['answer']], candidates=[self.answer], batch_size=self.batch_size)        

        self.results["score"] = score
        self.results["is_passing"] = bool(score > self.threshold)


def answer_score(answer_input: AnswerInput) -> AnswerResults:
    from database import db

    answer = Answer(answer_input, db)
    answer.score_answer()

    return AnswerResults(**answer.results)

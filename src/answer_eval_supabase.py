from models.answer import AnswerInput, AnswerResults
from supabase.client import Client
from transformers import logging
from pipelines.answer import AnswerPipeline
from connections.supabase import get_client

logging.set_verbosity_error()

answer_pipe = AnswerPipeline()


class Answer:
    def __init__(self, answer_input: AnswerInput, db: Client):
        # TODO: Change to use section slug
        # This process should be the same for all textbooks.
        if answer_input.textbook_name.name == "THINK_PYTHON":
            section_index = f"{answer_input.chapter_index:02}"
        elif answer_input.textbook_name.name in ["MACRO_ECON", "MATHIA"]:
            section_index = (
                f"{answer_input.chapter_index:02}-{answer_input.section_index:02}"
            )
        else:
            raise ValueError("Textbook not supported.")

        self.data = (
            db.table("subsections")
            .select("clean_text", "question", "answer")
            .eq("section_id", section_index)
            .eq("subsection", answer_input.subsection_index)
            .execute()
            .data
        )[0]

        self.answer = answer_input.answer
        self.results = {}

    def score_answer(self) -> None:
        """
        This currently returns passing score ONLY if both BLEURT and MPnet agree that it is passing
        """

        correct_answer = self.data["answer"]
        res = answer_pipe(self.answer, correct_answer)

        self.results["score"] = res
        if res < 2:
            self.results["is_passing"] = False
        else:
            self.results["is_passing"] = True


async def answer_score_supabase(answer_input: AnswerInput) -> AnswerResults:
    db = get_client(answer_input.textbook_name)

    answer = Answer(answer_input, db)
    answer.score_answer()

    return AnswerResults(**answer.results)

from models.answer import AnswerInput, AnswerResults
from supabase import Client
from transformers import logging
from pipelines.answer import AnswerPipeline

logging.set_verbosity_error()

answer_pipe = AnswerPipeline()


class Answer:
    def __init__(self, answer_input: AnswerInput, db: Client):
        # TODO: Change to use section slug
        # This process should be the same for all textbooks.
        if answer_input.textbook_name.name == "think_python_2e":
            section_index = f"{answer_input.section_index:02}"
        elif answer_input.textbook_name.name == "macroeconomics-2e":
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
        )[0]

        self.answer = answer_input.answer
        self.results = {}

    def score_answer(self) -> None:
        """Placeholder for BLEURT model implementation.
        Currently uses MPNet"""

        """

        TODO: INSERT CODE FOR BLEURT MODEL
        Replace MPNet pipeline below

        """

        correct_answer = self.data["answer"]
        res = answer_pipe.process(correct_answer, self.answer)
        # score = random.uniform(-1, 1)

        self.results["score"] = res["score"]
        self.results["is_passing"] = bool(int(res["label"][-1]))


def answer_score(answer_input: AnswerInput) -> AnswerResults:
    from database import get_client

    db = get_client(answer_input.textbook_name.name)

    answer = Answer(answer_input, db)
    answer.score_answer()

    return AnswerResults(**answer.results)

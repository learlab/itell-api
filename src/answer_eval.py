from models.answer import AnswerInput, AnswerResults
from supabase.client import Client
from transformers import logging
from pipelines.answer import AnswerPipeline
from src.database import get_client

logging.set_verbosity_error()


answer_pipe = AnswerPipeline()


class Answer:
    def __init__(self, answer_input: AnswerInput, db: Client):
        # TODO: Change to use section slug
        # This process should be the same for all textbooks.
        if answer_input.textbook_name.name == "THINK_PYTHON":
            section_index = f"{answer_input.chapter_index:02}"
        elif answer_input.textbook_name.name == "MACRO_ECON":
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
        '''
        This returns three objects in its results -
        logits - dictionary with raw bleurt score and mpnet label
        score - 0, 1, or 2 to say how correct the answer is
        is_passing - bool to describe whether it is passing (both models agree yes)
        '''
        # return logits from bleurt and label from MPnet
        correct_answer = self.data["answer"]
        res = answer_pipe.process(self.answer, correct_answer)
        self.results["logits"] = res

        # Get bleurt results
        bleurt_score = res['bleurt_score']
        if bleurt_score > 0.7:
            bleurt_res = True
        else:
            bleurt_res = False

        # Get MPnet results
        mpnet_score = res['mpnet_score']
        if mpnet_score == 'correct_answer':
            mpnet_res = True
        elif mpnet_score == 'incorrect_answer':
            mpnet_res = False

        # Majority voting
        if mpnet_res == True and bleurt_res == True:
            self.results["score"] = 2
        elif mpnet_res == False and bleurt_res == False:
            self.results["score"] = 0
        else:
            self.results["score"] = 1

        # is_passing results
        if self.results["score"] < 2:
            self.results["is_passing"] = False
        else:
            self.results["is_passing"] = True


async def answer_score(answer_input: AnswerInput) -> AnswerResults:
    db = get_client(answer_input.textbook_name)

    answer = Answer(answer_input, db)
    answer.score_answer()

    return AnswerResults(**answer.results)

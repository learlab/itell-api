from transformers import pipeline
from typing import Dict


class AnswerPipeline:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification", model="facehugger92/POE_QA_mpnetbase"
        )

    def process(self, correct_answer: str, text_input: str) -> Dict[str, str]:
        modified_text = f"The following two sentences are answers to the same question: {correct_answer}. {text_input}"  # noqa: E501
        res = self.classifier(modified_text)
        return res[0]  # type: ignore

from transformers import pipeline
from typing import Dict

class AnswerPipeline():
    def __init__(self):
        self.classifier = pipeline("text-classification", model="facehugger92/POE_QA_mpnetbase")

    def process(self, correct_answer, text_input):
        modified_text = f"The following two sentences are answers to the same question: {correct_answer}. {text_input}"
        res = self.classifier(modified_text)
        return res[0]
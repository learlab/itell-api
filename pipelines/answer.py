"""
Defines AnswerPipeline:
It loads a Bleurt model and an MPnet model for scoring a short answer.
The __call__ method takes a candidate and a reference answer as inputs.
If both models agree that the candidate is correct, return 2.
If the models disagree, return 1.
If both models agree that it is incorrect, return 0.
"""

from transformers import pipeline


class AnswerPipeline:
    mpnet_model = "tiedaar/short-answer-classification"
    bleurt_model = "vaiibhavgupta/finetuned-bleurt-large"
    bleurt_threshold = 0.7

    def __init__(self):
        self.mpnet_classifier = pipeline("text-classification", model=self.mpnet_model)
        self.bleurt_classifier = pipeline(
            "text-classification", model=self.bleurt_model
        )

    def __call__(self, candidate: str, reference: str) -> int:
        bleurt_sequence = f"{candidate}[SEP]{reference}"
        mpnet_sequence = f"{candidate}</s>{reference}"

        # Get bleurt results
        bleurt_result = self.bleurt_classifier(bleurt_sequence)
        if isinstance(bleurt_result, list) and isinstance(bleurt_result[0], dict):
            bleurt_score = bleurt_result[0]["score"]
        else:
            raise ValueError("BLEURT classifier returned an unexpected result.")

        # Get MPnet results
        result = self.mpnet_classifier(mpnet_sequence)
        if isinstance(result, list) and isinstance(result[0], dict):
            mpnet_score = result[0]["label"]
        else:
            raise ValueError("MPnet classifier returned an unexpected result.")

        bleurt_passing = True if bleurt_score >= self.bleurt_threshold else False
        mpnet_passing = True if mpnet_score == "correct_answer" else False

        if bleurt_passing and mpnet_passing:
            return 2
        elif bleurt_passing or mpnet_passing:
            return 1
        else:
            return 0

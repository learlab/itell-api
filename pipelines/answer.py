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
    mpnet_classifier = "tiedaar/short-answer-classification"
    bleurt_classifier = "vaiibhavgupta/finetuned-bleurt-large"
    bleurt_threshold = 0.7

    def __init__(self):
        self.mpnet_classifier = pipeline(
            "text-classification", model=self.mpnet_classifier
        )
        self.bleurt_classifier = pipeline(
            "text-classification", model=self.bleurt_classifier
        )

    def __call__(self, candidate: str, reference: str) -> int:
        bleurt_sequence = f"{candidate}[SEP]{reference}"
        mpnet_sequence = f"{candidate}</s>{reference}"

        # Get bleurt results
        bleurt_score = self.bleurt_classifier(bleurt_sequence)[0]["score"]
        if bleurt_score >= self.bleurt_threshold:
            bleurt_passing = True
        else:
            bleurt_passing = False

        # Get MPnet results
        mpnet_score = self.mpnet_classifier(mpnet_sequence)[0]["label"]
        if mpnet_score == "correct_answer":
            mpnet_passing = True
        elif mpnet_score == "incorrect_answer":
            mpnet_passing = False

        # Majority voting
        if bleurt_passing and mpnet_passing:
            return 2
        elif bleurt_passing or mpnet_passing:
            return 1
        else:
            return 0

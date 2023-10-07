"""
Defines AnswerPipeline:
It loads a Bleurt model and an MPnet model for scoring a short answer.
The __call__ method takes a candidate and a reference answer as inputs.
Return a dictionary with the bleurt score and the mpnet label
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

        bleurt_score = self.bleurt_classifier(bleurt_sequence)[0]['score']
        mpnet_score = self.mpnet_classifier(mpnet_sequence)[0]['label']

        return {'bleurt_score':bleurt_score, 'mpnet_score':mpnet_score}

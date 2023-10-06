"""
Defines AnswerPipeline:
It loads a Bleurt model and an MPnet model for scoring a short answer.
The __call__ method takes a candidate and a reference answer as inputs.
If both models agree that the candidate is correct, return 2.
If the models disagree, return 1.
If both models agree that it is incorrect, return 0.
"""

from transformers import pipeline
from typing import Dict

class AnswerPipeline:
    def __init__(self):
        self.mpnet_classifier = pipeline(
            "text-classification", model="tiedaar/short-answer-classification"
        )
        self.bleurt_classifier = pipeline(
            'text-classification', model="vaiibhavgupta/finetuned-bleurt-large"
        )
        
    
    def process(self, target: str, reference: str) -> Dict[str, str]:
        bleurt_sequence = f'{target}[SEP]{reference}'
        mpnet_sequence = f'{target}</s>{reference}'
        
        bleurt_score = self.bleurt_classifier(bleurt_sequence)[0]['score']
        mpnet_score = self.mpnet_classifier(mpnet_sequence)[0]['label']

        return {'bleurt_score':bleurt_score, 'mpnet_score':mpnet_score}
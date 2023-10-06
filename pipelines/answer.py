'''
This file creates a class called AnswerPipeline.
It loads a Bleurt model and an MPnet model for classifying whether an answer matches a correct answer.
The method process takes a candidate and a reference answer as inputs.
If both models agree that the candidate is correct, it returns a 2. If both models agree that it is incorrect, it returns a 1.
If the models disagree it returns a 2.
'''

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

from fastapi import HTTPException
from models.QA import QAInput, QAResults
import random


class QA:
    def __init__(self, qa_input: QAInput):
        self.chapter_index = qa_input.chapter_index
        self.section_index = qa_input.section_index
        self.subsection_index = qa_input.subsection_index
        self.section_index = f'{self.chapter_index:02}-{self.section_index:02}'
        self.subsection_index = f'{self.section_index}-{self.subsection_index:02}'

        self.QA_response = qa_input.QA_response
        self.threshold = 0.5 # Set threshold here

        self.results = {}

    def score_QA(self) -> None:
        '''Placeholder for BLEURT model implementation.
        Currently adds random float (between -1 and 1 to mimic BEURT)
        and random bool to result dict'''

        '''

        CODE FOR BLEURT MODEL
        replace random values below with actual scores

        '''

        score = random.uniform(-1, 1)

        self.results['score_float'] = score
        self.results['score_bool'] = bool(score>self.threshold)



def qa_score(qa_input: QAInput) -> QAResults:

    qa = QA(qa_input)
    qa.score_QA()

    return QAResults(**qa.results)

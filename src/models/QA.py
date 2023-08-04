from pydantic import BaseModel
from enum import Enum
from typing import Optional
from models.summary import TextbookNames


class QAInput(BaseModel):
    textbook_name: TextbookNames
    chapter_index: int
    section_index: int
    subsection_index: int # QAs are going to have to need subsection info
    QA_response: str


class QAResults(BaseModel):
    score_float: float # BLEURT score (or some other score) judging the correctness of response
    score_bool: bool # result_float classified into correct or incorrect answer

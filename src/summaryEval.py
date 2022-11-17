from transformers import pipeline
from .models.summary import SummaryInput

pipe = pipeline(
    "text-classification", model="tiedaar/SummaryContent", function_to_apply="none"
)

def get_score(summary_input: SummaryInput) -> float:
    return pipe(SummaryInput.text)[0]["score"]

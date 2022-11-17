from transformers import pipeline, logging
logging.set_verbosity_error()

from models.summary import SummaryInput

pipe = pipeline(
    "text-classification", model="tiedaar/SummaryContent", function_to_apply="none"
)

def get_score(summary_input: SummaryInput) -> float:
    return pipe(summary_input.text)[0]["score"]

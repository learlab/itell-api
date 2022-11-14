from transformers import pipeline

pipe = pipeline(
    "text-classification", model="tiedaar/SummaryContent", function_to_apply="none"
)


def get_score(text: str) -> float:
    return pipe(text)[0]["score"]

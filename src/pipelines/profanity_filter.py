from pathlib import Path

from spacy.tokens import Doc

with open(Path("assets/offensive-words.txt"), "r") as data:
    offensive_words = set(data.read().splitlines())


def profanity_filter(doc: Doc) -> bool:
    """Returns True if doc contains offensive words."""
    return any(tok.lower_ in offensive_words for tok in doc)

from spacy.tokens import Doc


def trigrams(doc: Doc) -> set[tuple[int, ...]]:
    """Get trigrams from a Spacy Doc
    Excludes stop words.
    Uses lowercase form of tokens.
    Uses int representation of token instead of string.
    """
    tokens = [t.lower for t in doc if not t.is_stop]
    return {tuple(tokens[i : i + 3]) for i in range(len(tokens) - 2)}


def score_containment(source: Doc, derivative: Doc) -> float:
    """Calculate containment score between a source text and a derivative
    text. Calculated as the intersection of unique trigrams divided by the
    number of unique trigrams in the derivative text. Values range from 0
    to 1, with 1 being completely copied."""
    src = trigrams(source)
    deriv = trigrams(derivative)
    try:
        containment = len(src.intersection(deriv)) / len(deriv)
        return round(containment, 4)
    except ZeroDivisionError:
        return 1.0

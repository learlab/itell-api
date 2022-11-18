from nltk import download as nltk_download
from nltk import trigrams, word_tokenize

from models.summary import SummaryInput

nltk_download("punkt")


def get_trigrams(text):
    return set(trigrams(word_tokenize(text)))


def containment_score(summary_input):
    src = get_trigrams(summary_input.source)
    txt = get_trigrams(summary_input.text)
    try:
        containment = len(src.intersection(txt)) / len(txt)
        return round(containment, 4)
    except ZeroDivisionError:
        return 1

from nltk import trigrams, word_tokenize
from .models.summary import SummaryInput

def get_trigrams(text):
    return set(trigrams(word_tokenize(text)))

def containment_score(summary_input):
    src = get_trigrams(summary_input.source)
    txt = get_trigrams(summary_input.text)
    containment = len(src.intersection(txt))/len(txt)
    return round(containment, 4)
  
if __name__ == "__main__":
    summary_input = SummaryInput(
        source='The most important topic in economics is supply and demand',
        text='Economics is about supply and demand.'
    )

    print(containment_score(summary_input))
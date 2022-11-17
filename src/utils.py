from nltk import trigrams, word_tokenize

def get_trigrams(text):
    return set(trigrams(word_tokenize(text)))

def containment_score(summary_input):
    src = get_trigrams(summary_input.source)
    txt = get_trigrams(summary_input.text)
    containment = len(src.intersection(txt))/len(txt)
    return round(containment, 4)
  

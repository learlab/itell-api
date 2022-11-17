import numpy as np

def tokenize(text):
    return np.array(text.split())

def containment_score(summary_input):
    src = tokenize(summary_input.source)
    txt = tokenize(summary_input.text)
    containment = len(src.intersection(txt))/len(txt)
    return round(containment, 4)
  

from transformers import pipeline, logging
logging.set_verbosity_error()

import nltk
from nltk.corpus import stopwords
from gensim.models import Doc2Vec
from scipy import spatial

from models.summary import SummaryInput, SummaryResults

english_stop_words = stopwords.words('english')

# a textbook split into sections
with open('../assets/macroeconomics_2e_section.json', "r") as data:
    source_dict = json.loads(data.read())

# a custom pre-trained doc2vec model (gensim)
doc2vec_model = Doc2Vec.load('../assets/doc2vec_model') 

# Huggingface pipelines to score section summaries
content_pipe = pipeline('text-classification', model='tiedaar/summary-longformer-content', function_to_apply='none')
wording_pipe = pipeline('text-classification', model='tiedaar/summary-longformer-wording', function_to_apply='none')

def tokenize_text(text):
    return [tok for tok in nltk.word_tokenize(text) if tok not in english_stop_words]

def similarity_score(summary, source) -> float:
    '''Return semantic similarity score based on summary and source text.
    summary: str
    source: str
    '''
    summary_embedding = doc2vec_model.infer_vector(tokenize_text(summary))
    source_embedding = doc2vec_model.infer_vector(tokenize_text(source))
    return 1 - spatial.distance.cosine(summary_embedding, source_embedding)

def summary_score(summary, source) -> dict[float]:
    '''Return summary evlauation scores based on summary and source text.
    summary: str
    source: str
    '''
    input_text = summary + '</s>' + source
    results_dict = {}
    results_dict['content'] = content_pipe(input_text)
    results_dict['wording'] = wording_pipe(input_text)
    return results_dict
    


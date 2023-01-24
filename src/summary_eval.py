from transformers import pipeline, logging
logging.set_verbosity_error()

from gensim.models import Doc2Vec
from scipy import spatial
from nltk.corpus import stopwords
from nltk import trigrams, word_tokenize
from pathlib import Path
import json

from models.summary import SummaryInput, SummaryResults

english_stop_words = stopwords.words('english')

with open(Path('assets/macroeconomics_2e_sections.json'), 'r') as data:
    source_dict = json.loads(data.read())

# a custom pre-trained doc2vec model (gensim)
doc2vec_model = Doc2Vec.load(str(Path('assets/doc2vec_model')))

# Huggingface pipelines to score section summaries
content_pipe = pipeline('text-classification', model='tiedaar/summary-longformer-content', function_to_apply='none')
wording_pipe = pipeline('text-classification', model='tiedaar/summary-longformer-wording', function_to_apply='none')

def tokenize_text(text: str):
    return [tok for tok in word_tokenize(text) if tok not in english_stop_words]

def get_trigrams(text: str):
    return set(trigrams(tokenize_text(text)))

def containment_score(summary_input: SummaryInput) -> float:
    src = get_trigrams(summary_input.source)
    txt = get_trigrams(summary_input.summary)
    try:
        containment = len(src.intersection(txt)) / len(txt)
        return round(containment, 4)
    except ZeroDivisionError:
        return 1.0

def similarity_score(summary_input: SummaryInput) -> float:
    '''Return semantic similarity score based on summary and source text.
    '''
    summary_embedding = doc2vec_model.infer_vector(tokenize_text(summary_input.summary))
    source_embedding = doc2vec_model.infer_vector(tokenize_text(summary_input.source))
    return 1 - spatial.distance.cosine(summary_embedding, source_embedding)

def analytic_score(summary_input: SummaryInput) -> tuple[float]:
    '''Return summary evlauation scores based on summary and source text.
    '''
    input_text = summary_input.summary + '</s>' + summary_input.source
    return (
        content_pipe(input_text, truncation=True, max_length=4096)[0]['score'],
        wording_pipe(input_text, truncation=True, max_length=4096)[0]['score']
        )

def summary_score(summary_input: SummaryInput) -> SummaryResults:
    '''Checks summary for text copied from the source and for semantic relevance to the source text.
    If it passes these checks, score the summary using a Huggingface pipeline.
    '''

    section_code = f'{summary_input.chapter_index:02}-{summary_input.section_index}'
    summary_input.source = source_dict[section_code]

    summary_results = SummaryResults(
        containment = containment_score(summary_input),
        similarity = similarity_score(summary_input)
        )

    if summary_results.containment > 0.6 or summary_results.similarity < 0.3:
        return summary_results

    content, wording = analytic_score(summary_input)
    summary_results.content = content
    summary_results.wording = wording

    return summary_results



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
def make_pipe(model_name: str):
    return pipeline('text-classification', model=model_name,
                    function_to_apply='none')
content_pipe = make_pipe('tiedaar/summary-longformer-content')
wording_pipe = make_pipe('tiedaar/summary-longformer-wording')

def tokenize_text(text: str):
    return [tok for tok in word_tokenize(text.lower())
            if tok not in english_stop_words]

def get_trigrams(text: str):
    return set(trigrams(tokenize_text(text)))

def containment_score(
    summary_input: SummaryInput,
    source: str = None, summary: str = None
) -> float:
    '''Calculate containment score between a source text and a derivative text.
    Calculated as the intersection of unique trigrams divided by the number if 
    unique trigrams in the derivative text.
    Values range from 0 to 1, with 1 being completely copied.
    Allows for source and summary to be manually input for testing purposes.'''
    if summary_input:
        source, summary = summary_input.source, summary_input.summary
    src = get_trigrams(source)
    txt = get_trigrams(summary)
    try:
        containment = len(src.intersection(txt)) / len(txt)
        return round(containment, 4)
    except ZeroDivisionError:
        return 1.0

def similarity_score(summary_input: SummaryInput) -> float:
    '''Return semantic similarity score based on summary and source text.
    '''
    source_tokens = tokenize_text(summary_input.source)
    summary_tokens = tokenize_text(summary_input.summary)
    source_embedding = doc2vec_model.infer_vector(source_tokens)
    summary_embedding = doc2vec_model.infer_vector(summary_tokens)
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
    '''Checks summary for text copied from the source and for semantic 
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    '''
    section_code = f'{summary_input.chapter_index:02}-\
        {summary_input.section_index}'
    summary_input.source = source_dict[section_code]

    summary_results = SummaryResults(
        containment = containment_score(summary_input),
        similarity = similarity_score(summary_input)
        )

    if summary_results.containment > 0.5 or summary_results.similarity < 0.3:
        return summary_results

    content, wording = analytic_score(summary_input)
    summary_results.content = content
    summary_results.wording = wording

    return summary_results

if __name__ == "__main__":
    source='Hello my name is from the future, but I live in the past.'
    summary='Hello my name is from the future.'
    print(containment_score(None, source=source, summary=summary))
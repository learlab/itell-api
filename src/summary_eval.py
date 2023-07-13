from fastapi import HTTPException

from transformers import logging

from gensim.models import Doc2Vec
from scipy import spatial
from nltk import trigrams

from pathlib import Path
import json
import random

from models.summary import SummaryInput, SummaryResults
from pipelines.scoring import ScoringPipeline

import spacy
nlp = spacy.load('en_core_web_sm')

logging.set_verbosity_error()

with open(Path('assets/offensive-words.txt'), 'r') as data:
    offensive_words = set(data.read().splitlines())

doc2vec_model = Doc2Vec.load(str(Path('assets/doc2vec-model')))

content_pipe = ScoringPipeline('tiedaar/longformer-content-global')
wording_pipe = ScoringPipeline('tiedaar/longformer-wording-global')


class Summary:
    def __init__(self, summary_input: SummaryInput):
        self.textbook_name = summary_input.textbook_name
        self.chapter_index = summary_input.chapter_index
        self.section_index = summary_input.section_index
        self.section_code = f'{self.chapter_index:02}-{self.section_index:02}'
        self.summary = summary_input.summary

        source_dict_path = Path(f'assets/{self.textbook_name}-sections.json')
        if not source_dict_path.exists():
            raise HTTPException(
                status_code=500,
                detail='The server validated the textbook name but failed to '
                f'locate the relevant resource at {source_dict_path}.',
                )
            
        with open(source_dict_path, 'r') as data:
            source_dict = json.loads(data.read())
            
        self.source = source_dict[self.section_code]['text']
        self.keyphrases = source_dict[self.section_code]['keyphrases']

        self.results = {}

        # intermediate objects for scoring
        self.input_text = self.summary + '</s>' + self.source
        self.summary_doc = nlp(self.summary)
        self.source_doc = nlp(self.source)
        self.keyphrase_docs = [nlp(keyphrase) for keyphrase in self.keyphrases]

    def score_containment(self) -> None:
        '''Calculate containment score between a source text and a derivative
        text. Calculated as the intersection of unique trigrams divided by the
        number of unique trigrams in the derivative text. Values range from 0
        to 1, with 1 being completely copied.'''

        src = set(trigrams(
            [t.text for t in self.source_doc if not t.is_stop]))
        txt = set(trigrams(
            [t.text for t in self.summary_doc if not t.is_stop]))
        try:
            containment = len(src.intersection(txt)) / len(txt)
            self.results['containment'] = round(containment, 4)
        except ZeroDivisionError:
            self.results['containment'] = 1.0

    def score_similarity(self) -> None:
        '''Return semantic similarity score based on summary and source text.
        '''
        source_embed = doc2vec_model.infer_vector(
            [t.text for t in self.source_doc if not t.is_stop])
        summary_embed = doc2vec_model.infer_vector(
            [t.text for t in self.summary_doc if not t.is_stop]
        )
        self.results['similarity'] = 1 - spatial.distance.cosine(summary_embed,
                                                                 source_embed)

    def score_content(self) -> None:
        '''Return content score based on summary and source text.
        '''
        self.results['content'] = content_pipe(self.input_text,
                                               truncation=True,
                                               max_length=4096)[0]['score']

    def score_wording(self) -> None:
        '''Return wording score based on summary and source text.
        '''
        self.results['wording'] = wording_pipe(self.input_text,
                                               truncation=True,
                                               max_length=4096)[0]['score']

    def extract_keyphrases(self) -> None:
        '''Return keyphrases that were included in the summary and suggests
        keyphrases that were not included.
        '''
        included_keyphrases = set()
        suggested_keyphrases = list()

        summary_lemmas = {t.lemma_ for t in self.summary_doc if not t.is_stop}

        for keyphrase in self.keyphrase_docs:
            key_lemmas = {t.lemma_ for t in keyphrase if not t.is_stop}
            keyphrase_included = not summary_lemmas.isdisjoint(key_lemmas)
            if keyphrase_included:
                included_keyphrases.add(keyphrase.text)
            else:
                suggested_keyphrases.append(keyphrase.text)

        self.results['included_keyphrases'] = included_keyphrases
        self.results['suggested_keyphrases'] = random.sample(
            suggested_keyphrases, 3
            )

    def check_profanity(self) -> None:
        '''Return True if summary contains profanity.
        '''
        summary_words = {t.lower_ for t in self.summary_doc if not t.is_stop}
        is_clean = summary_words.isdisjoint(offensive_words)
        self.results['profanity'] = not is_clean


def summary_score(summary_input: SummaryInput) -> SummaryResults:
    '''Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    '''

    summary = Summary(summary_input)

    summary.score_containment()
    summary.score_similarity()
    summary.check_profanity()
    summary.extract_keyphrases()

    junk_filter = (summary.results['containment'] > 0.5
                   or summary.results['similarity'] < 0.3
                   or summary.results['profanity'])

    if junk_filter:
        return SummaryResults(**summary.results)

    else:
        summary.score_content()
        summary.score_wording()
        return SummaryResults(**summary.results)

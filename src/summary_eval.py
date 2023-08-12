from transformers import logging

from gensim.models import Doc2Vec
from scipy import spatial
from nltk import trigrams

from pathlib import Path
from itertools import chain
import random

from models.summary import SummaryInput, SummaryResults
from pipelines.summary import SummaryPipeline
from supabase import Client

import spacy

nlp = spacy.load("en_core_web_sm")

logging.set_verbosity_error()

with open(Path("assets/offensive-words.txt"), "r") as data:
    offensive_words = set(data.read().splitlines())

doc2vec_model = Doc2Vec.load(str(Path("assets/doc2vec-model")))

content_pipe = SummaryPipeline("tiedaar/longformer-content-global")
wording_pipe = SummaryPipeline("tiedaar/longformer-wording-global")


class Summary:
    def __init__(self, summary_input: SummaryInput, db: Client):
        section_index = (
            f"{summary_input.chapter_index:02}" f"-{summary_input.section_index:02}"
        )

        # Fetch content and restructure data
        data = (
            db.table("subsections")
            .select("clean_text", "keyphrases")
            .eq("section_id", section_index)
            .execute()
            .data
        )
        clean_text = "\n\n".join([str(row["clean_text"]) for row in data])
        keyphrases = [row["keyphrases"] for row in data]

        # Create SpaCy objects
        self.source = nlp(clean_text)
        self.keyphrases = list(nlp.pipe(chain(*keyphrases)))
        self.summary = nlp(summary_input.summary)

        self.results = {}

        # intermediate objects for scoring
        self.input_text = self.summary.text + "</s>" + self.source.text

    def score_containment(self) -> None:
        """Calculate containment score between a source text and a derivative
        text. Calculated as the intersection of unique trigrams divided by the
        number of unique trigrams in the derivative text. Values range from 0
        to 1, with 1 being completely copied."""

        src = set(trigrams([t.text for t in self.source if not t.is_stop]))
        txt = set(trigrams([t.text for t in self.summary if not t.is_stop]))
        try:
            containment = len(src.intersection(txt)) / len(txt)
            self.results["containment"] = round(containment, 4)
        except ZeroDivisionError:
            self.results["containment"] = 1.0

    def score_similarity(self) -> None:
        """Return semantic similarity score based on summary and source text"""
        source_embed = doc2vec_model.infer_vector(
            [t.text for t in self.source if not t.is_stop]
        )
        summary_embed = doc2vec_model.infer_vector(
            [t.text for t in self.summary if not t.is_stop]
        )
        self.results["similarity"] = 1 - spatial.distance.cosine(
            summary_embed, source_embed
        )

    def score_content(self) -> None:
        """Return content score based on summary and source text."""
        self.results["content"] = content_pipe(
            self.input_text, truncation=True, max_length=4096
        )[0]["score"]

    def score_wording(self) -> None:
        """Return wording score based on summary and source text."""
        self.results["wording"] = wording_pipe(
            self.input_text, truncation=True, max_length=4096
        )[0]["score"]

    def extract_keyphrases(self) -> None:
        """Return keyphrases that were included in the summary and suggests
        keyphrases that were not included.
        """
        included_keyphrases = set()
        suggested_keyphrases = list()

        summary_lemmas = {t.lemma_ for t in self.summary if not t.is_stop}

        for keyphrase in self.keyphrases:
            key_lemmas = {t.lemma_ for t in keyphrase if not t.is_stop}
            keyphrase_included = not summary_lemmas.isdisjoint(key_lemmas)
            if keyphrase_included:
                included_keyphrases.add(keyphrase.text)
            else:
                suggested_keyphrases.append(keyphrase.text)

        self.results["included_keyphrases"] = included_keyphrases
        self.results["suggested_keyphrases"] = random.sample(suggested_keyphrases, 3)

    def check_profanity(self) -> None:
        """Return True if summary contains profanity."""
        summary_words = {t.lower_ for t in self.summary if not t.is_stop}
        is_clean = summary_words.isdisjoint(offensive_words)
        self.results["profanity"] = not is_clean


def summary_score(summary_input: SummaryInput) -> SummaryResults:
    """Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    """
    from database import db

    summary = Summary(summary_input, db)

    summary.score_containment()
    summary.score_similarity()
    summary.check_profanity()
    summary.extract_keyphrases()

    junk_filter = (
        summary.results["containment"] > 0.5
        or summary.results["similarity"] < 0.3
        or summary.results["profanity"]
    )

    if junk_filter:
        return SummaryResults(**summary.results)

    else:
        summary.score_content()
        summary.score_wording()
        return SummaryResults(**summary.results)

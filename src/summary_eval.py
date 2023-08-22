import random
import re
from pathlib import Path

import spacy
from gensim.models import Doc2Vec
from nltk import trigrams
from scipy import spatial
from supabase import Client
from transformers import logging

from models.summary import SummaryInput, SummaryResults
from pipelines.summary import SummaryPipeline

nlp = spacy.load("en_core_web_sm", disable=["ner"])

logging.set_verbosity_error()

doc2vec_model = Doc2Vec.load(str(Path("assets/doc2vec-model")))

content_pipe = SummaryPipeline("tiedaar/longformer-content-global")
wording_pipe = SummaryPipeline("tiedaar/longformer-wording-global")


class Summary:
    def __init__(self, summary_input: SummaryInput, db: Client):

        # TODO: Change to use section slug
        # This process should be the same for all textbooks.
        if summary_input.textbook_name == "think_python_2e":
            section_index = f"{summary_input.section_index:02}"
        elif summary_input.textbook_name == "macroeconomics-2e":
            section_index = (
                f"{summary_input.chapter_index:02}-{summary_input.section_index:02}"
            )

        # Fetch content and restructure data
        data = (
            db.table("subsections")
            .select("slug", "clean_text", "keyphrases")
            .eq("section_id", section_index)
            .execute()
            .data
        )

        clean_text = "\n\n".join([str(row["clean_text"]) for row in data])

        # Create SpaCy objects
        self.source = nlp(clean_text)
        self.summary = nlp(summary_input.summary)

        # Organize and Process keyphrases:
        self.chunks = {}
        for row in data:
            self.chunks[row["slug"]] = {
                "keyphrases": list(nlp.pipe(row["keyphrases"])),
                # chunks with no focus time record are assigned 1 seconds
                "focus_time": summary_input.focus_time.get(row["slug"], 1),
            }

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

    def suggest_keyphrases(self) -> None:
        """Return keyphrases that were included in the summary and suggests
        keyphrases that were not included.
        """
        included_keyphrases = list()
        suggested_keyphrases = list()
        weights = list()

        summary_lemmas = " ".join(
            [t.lemma_.lower() for t in self.summary if not t.is_stop]
        )

        for chunk in self.chunks.values():
            for keyphrase in chunk["keyphrases"]:
                keyphrase_lemmas = [t.lemma_ for t in keyphrase if not t.is_stop]
                keyphrase_included = re.search(
                    re.escape(r" ".join(keyphrase_lemmas)),
                    summary_lemmas,
                    re.IGNORECASE,
                )
                if keyphrase_included:
                    # keyphrase is included in summary
                    included_keyphrases.append(keyphrase.text)
                elif keyphrase.text in suggested_keyphrases:
                    # keyphrase has already been suggested
                    # increase the weight of this keyphrase suggestion
                    keyphrase_index = suggested_keyphrases.index(keyphrase.text)
                    weights[keyphrase_index] += 1 / chunk["focus_time"]
                else:
                    # New keyphrase suggestion
                    suggested_keyphrases.append(keyphrase.text)
                    # weight keyphrase suggestions by inverse focus time
                    weights.append(1 / chunk["focus_time"])

        self.results["included_keyphrases"] = included_keyphrases
        self.results["suggested_keyphrases"] = random.choices(
            suggested_keyphrases, k=3, weights=weights
        )


def summary_score(summary_input: SummaryInput) -> SummaryResults:
    """Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    """
    from database import get_client
    db = get_client(summary_input.textbook_name)

    summary = Summary(summary_input, db)

    summary.score_containment()
    summary.score_similarity()
    summary.suggest_keyphrases()

    junk_filter = (
        summary.results["containment"] > 0.5 or summary.results["similarity"] < 0.3
    )

    if junk_filter:
        return SummaryResults(**summary.results)

    else:
        summary.score_content()
        summary.score_wording()
        return SummaryResults(**summary.results)

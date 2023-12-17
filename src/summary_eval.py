from .models.summary import SummaryInputStrapi, SummaryResults
from .pipelines.summary import SummaryPipeline
from .pipelines.similarity import semantic_similarity
from .connections.strapi import Strapi


import random
import re

import pycld2 as cld2
import spacy

# from generate_embeddings import generate_embedding, max_similarity
from nltk import trigrams
from transformers import logging


nlp = spacy.load("en_core_web_sm", disable=["ner"])

logging.set_verbosity_error()


content_pipe = SummaryPipeline("tiedaar/longformer-content-global")
wording_pipe = SummaryPipeline("tiedaar/longformer-wording-global")


class Summary:
    def __init__(
        self, summary: str, components: list[dict[str, str]], focus_time: dict[str, int]
    ):
        self.focus_time = focus_time
        self.components = components
        clean_text = "\n\n".join(
            [component["CleanText"] for component in self.components]
        )

        # Create SpaCy objects
        self.source = nlp(clean_text)
        self.summary = nlp(summary)

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

        self.results["similarity"] = semantic_similarity(
            [t.text for t in self.source if not t.is_stop],
            [t.text for t in self.summary if not t.is_stop],
        )

    def score_content(self) -> None:
        """Return content score based on summary and source text."""
        res = content_pipe(self.input_text, truncation=True, max_length=4096)
        self.results["content"] = res[0]["score"]  # type: ignore

    def score_wording(self) -> None:
        """Return wording score based on summary and source text."""
        res = wording_pipe(self.input_text, truncation=True, max_length=4096)
        self.results["wording"] = res[0]["score"]  # type: ignore

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

        for chunk in self.components:
            if not chunk.get("KeyPhrase"):
                continue

            chunk_slug = chunk["Slug"]
            # avoid zero division
            focus_time = max(self.focus_time.get(chunk_slug, 1), 1)

            for keyphrase in nlp.pipe(chunk["KeyPhrase"]):
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
                    weights[keyphrase_index] += 1 / focus_time
                else:
                    # New keyphrase suggestion
                    suggested_keyphrases.append(keyphrase.text)
                    # weight keyphrase suggestions by inverse focus time
                    weights.append(1 / focus_time)

        self.results["included_keyphrases"] = included_keyphrases
        self.results["suggested_keyphrases"] = random.choices(
            suggested_keyphrases, k=3, weights=weights
        )


async def summary_score(summary_input: SummaryInputStrapi) -> SummaryResults:
    """Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    """
    strapi = Strapi()

    response = await strapi.fetch(
        f"/api/pages?filters[slug][$eq]={summary_input.page_slug}&populate[Content]=*"
    )

    content = response["data"][0]["attributes"]["Content"]

    summary = Summary(
        summary_input.summary,
        content,
        summary_input.focus_time,
    )

    summary.score_containment()
    summary.score_similarity()
    summary.suggest_keyphrases()

    summary.results["english"] = True
    is_detection_reliable, _, details = cld2.detect(summary_input.summary)
    if is_detection_reliable and details[0][0] != "ENGLISH":
        summary.results["english"] = False

    junk_filter = (
        summary.results["containment"] > 0.5
        or summary.results["similarity"] < 0.3
        or not summary.results["english"]
    )

    if junk_filter:
        return SummaryResults(**summary.results)

    else:
        summary.score_content()
        summary.score_wording()
        return SummaryResults(**summary.results)

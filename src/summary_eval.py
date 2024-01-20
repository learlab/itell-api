from .models.summary import SummaryInputStrapi, SummaryResults
from .models.strapi import Chunk
from typing import Union
from .pipelines.summary import SummaryPipeline
from .pipelines.similarity import semantic_similarity
from .connections.strapi import Strapi

import random
import re
import gcld3
import spacy
from spacy.tokens import Doc
from nltk import trigrams
from transformers import logging

logging.set_verbosity_error()

strapi = Strapi()

nlp = spacy.load("en_core_web_sm", disable=["ner"])
content_pipe = SummaryPipeline("tiedaar/longformer-content-global")
wording_pipe = SummaryPipeline("tiedaar/longformer-wording-global")
detector = gcld3.NNetLanguageIdentifier(min_num_bytes=0, max_num_bytes=1000)


def score_containment(source: Doc, derivative: Doc) -> float:
    """Calculate containment score between a source text and a derivative
    text. Calculated as the intersection of unique trigrams divided by the
    number of unique trigrams in the derivative text. Values range from 0
    to 1, with 1 being completely copied."""
    src = set(trigrams([t.text for t in source if not t.is_stop]))
    deriv = set(trigrams([t.text for t in derivative if not t.is_stop]))
    try:
        containment = len(src.intersection(deriv)) / len(deriv)
        return round(containment, 4)
    except ZeroDivisionError:
        return 1.0


class Summary:
    def __init__(
        self,
        summary: str,
        chunks: list[Chunk],
        focus_time: dict[str, int],
        chat_history: Union[str, None] = None,
    ):
        self.focus_time = focus_time
        self.chunks = chunks
        clean_text = "\n\n".join([chunk.CleanText for chunk in self.chunks])

        # Create SpaCy objects
        self.source = nlp(clean_text)
        self.summary = nlp(summary)
        if chat_history:
            self.chat_history = nlp(chat_history)
        else:
            self.chat_history = None

        self.results = {}

        # intermediate objects for scoring
        self.input_text = self.summary.text + "</s>" + self.source.text

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

        for chunk in self.chunks:
            if not chunk.KeyPhrase:
                continue

            # avoid zero division
            focus_time = max(self.focus_time.get(chunk.Slug, 1), 1)

            for keyphrase in nlp.pipe(chunk.KeyPhrase):
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

    chunks = await strapi.get_chunks(summary_input.page_slug)

    summary = Summary(
        summary_input.summary,
        chunks,
        summary_input.focus_time,
        summary_input.chat_history
    )

    summary.results["containment"] = score_containment(summary.source, summary.summary)
    if summary.chat_history:
        summary.results["containment_chat"] = score_containment(
            summary.chat_history, summary.summary
        )
    summary.score_similarity()
    summary.suggest_keyphrases()

    summary.results["english"] = True
    result = detector.FindLanguage(text=summary_input.summary)
    if result.is_reliable and result.language != "en":
        summary.results["english"] = False

    junk_filter = (
        summary.results["containment"] > 0.5
        or summary.results.get("containment_chat", 0) > 0.5
        or summary.results["similarity"] < 0.3
        or not summary.results["english"]
    )

    if junk_filter:
        return SummaryResults(**summary.results)

    else:
        summary.score_content()
        summary.score_wording()
        return SummaryResults(**summary.results)

from .models.summary import SummaryInputStrapi, Summary
from spacy.tokens import Doc

from .pipelines.nlp import nlp
from .pipelines.embed import EmbeddingPipeline
from .pipelines.containment import score_containment
from .pipelines.summary import SummaryPipeline
from .pipelines.suggest_keyphrases import suggest_keyphrases
from .connections.strapi import Strapi

import gcld3
from transformers import logging

logging.set_verbosity_error()

strapi = Strapi()

content_pipe = SummaryPipeline("tiedaar/longformer-content-global")
wording_pipe = SummaryPipeline("tiedaar/longformer-wording-global")
embedding_pipe = EmbeddingPipeline()
detector = gcld3.NNetLanguageIdentifier(  # type: ignore
    min_num_bytes=0, max_num_bytes=1000
)


async def summary_score(summary_input: SummaryInputStrapi, do_stairs=False) -> Summary:
    """Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    """

    # Retrieve chunks from Strapi and weight them
    # 3.33 words per second is an average reading pace
    chunks = await strapi.get_chunks(summary_input.page_slug)
    chunk_docs = list(nlp.pipe([chunk.CleanText for chunk in chunks]))
    for chunk, chunk_doc in zip(chunks, chunk_docs):
        focus_time = max(summary_input.focus_time.get(chunk.Slug, 1), 1)
        chunk.weight = 3.33 * (focus_time / len(chunk_doc))

    # Create summary data object
    summary = Summary(
        summary=nlp(summary_input.summary),
        source=Doc.from_docs(chunk_docs),  # combine into a single doc
        chunks=chunks,
        page_slug=summary_input.page_slug,
        chat_history=nlp(summary_input.chat_history)
        if summary_input.chat_history
        else None,
    )

    # Check if summary borrows language from source
    summary.results["containment"] = score_containment(summary.source, summary.summary)

    # Check if summary borrows language from chat history
    if summary.chat_history:
        summary.results["containment_chat"] = score_containment(
            summary.chat_history, summary.summary
        )

    # Check if summary is similar to source text
    summary.results["similarity"] = embedding_pipe.score_similarity(
        summary.source.text, summary.summary.text
    )

    # Generate keyphrase suggestions
    included, suggested = suggest_keyphrases(summary.summary, summary.chunks)
    summary.results["included_keyphrases"] = included
    summary.results["suggested_keyphrases"] = suggested

    # Check if summary is in English
    summary.results["english"] = True
    lang_result = detector.FindLanguage(text=summary_input.summary)
    if lang_result.is_reliable and lang_result.language != "en":
        summary.results["english"] = False

    # Check if summary fails to meet minimum requirements
    junk_filter = (
        summary.results["containment"] > 0.5
        or summary.results.get("containment_chat", 0) > 0.5
        or summary.results["similarity"] < 0.3
        or not summary.results["english"]
    )

    if junk_filter:
        return summary

    # Summary meets minimum requirements. Score it.
    input_text = summary.summary.text + "</s>" + summary.source.text
    summary.results["content"] = content_pipe(input_text)
    summary.results["wording"] = wording_pipe(input_text)

    return summary

import gcld3
from transformers import logging

from ..dependencies.strapi import Strapi
from ..dependencies.faiss import FAISS
from ..pipelines.containment import score_containment
from ..pipelines.keyphrases import suggest_keyphrases
from ..pipelines.model_runner import Pipes
from ..pipelines.profanity_filter import profanity_filter
from ..pipelines.summary import LongformerPipeline, SummaryPipeline
from ..schemas.strapi import Chunk
from ..schemas.summary import (
    ChunkWithWeight,
    Summary,
    SummaryInputStrapi,
    SummaryResults,
)

logging.set_verbosity_error()

detector = gcld3.NNetLanguageIdentifier(  # type: ignore
    min_num_bytes=0, max_num_bytes=1000
)


def weight_chunks(chunks: list[Chunk], focus_time_dict: dict) -> list[ChunkWithWeight]:
    """Weight chunks based on focus time"""
    weighted_chunks = []
    for chunk in chunks:
        if not chunk.component_type == "page.chunk":
            continue
        focus_time = max(focus_time_dict.get(chunk.Slug, 1), 1)
        word_count = len(chunk.CleanText.split(" "))
        weight = 3.33 * (focus_time / word_count)
        weighted_chunks.append(
            ChunkWithWeight(**chunk.model_dump(by_alias=True), weight=weight)
        )
    return weighted_chunks


async def summary_score(
    summary_input: SummaryInputStrapi,
    strapi: Strapi,
    faiss: FAISS,
    pipes: Pipes,
) -> tuple[Summary, SummaryResults]:
    """Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    """

    # Retrieve chunks from Strapi and weight them
    # 3.33 words per second is an average reading pace
    chunks = await strapi.get_chunks(summary_input.page_slug)

    source_doc = await pipes.nlp.remote(
        "\n".join([chunk.CleanText for chunk in chunks])
    )

    weighted_chunks = weight_chunks(chunks, summary_input.focus_time)

    bot_messages = None
    if summary_input.chat_history:
        bot_messages = "\n".join(
            [msg.text for msg in summary_input.chat_history if msg.agent == "bot"]
        )

    # Create summary data object
    summary = Summary(
        summary=await pipes.nlp.remote(summary_input.summary),
        source=source_doc,
        chunks=weighted_chunks,
        page_slug=summary_input.page_slug,
        chat_history=summary_input.chat_history,
        bot_messages=await pipes.nlp.remote(bot_messages) if bot_messages else None,
        excluded_chunks=(
            summary_input.excluded_chunks if summary_input.excluded_chunks else []
        ),
    )

    results = {}

    # Check if summary borrows language from source
    results["containment"] = score_containment(summary.source, summary.summary)

    # Check if summary borrows language from chat history
    if summary.bot_messages:
        results["containment_chat"] = score_containment(
            summary.bot_messages, summary.summary
        )

    # Check if summary is similar to source text
    results["similarity"] = (
        await faiss.page_similarity(summary.summary.text, summary.page_slug)
    )  # adding 0.15 to bring similarity score in line with old doc2vec model
    # Generate keyphrase suggestions
    included, suggested = await suggest_keyphrases(
        summary.summary, summary.chunks, pipes
    )
    results["included_keyphrases"] = included
    results["suggested_keyphrases"] = suggested

    # Check if summary is in English
    results["english"] = True
    lang_result = detector.FindLanguage(text=summary_input.summary)
    if lang_result.is_reliable and lang_result.language != "en":
        results["english"] = False

    # Check if summary contains profanity
    results["profanity"] = profanity_filter(summary.summary)

    # Check if summary fails to meet minimum requirements
    junk_filter = (
        results["containment"] > 0.6
        or results.get("containment_chat", 0.0) > 0.6
        or results["similarity"] > 1.15
        or results["english"] is False
        or results["profanity"] is True
    )

    if junk_filter:
        return summary, SummaryResults(**results)

    # Summary meets minimum requirements. Score it.
    input_text = summary.summary.text + "</s>" + summary.source.text

    results["content"] = await pipes.content.remote(input_text)
    results["language"] = await pipes.language.remote(summary.summary.text)

    return summary, SummaryResults(**results)

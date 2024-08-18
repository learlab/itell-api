import gcld3
from spacy.tokens import Doc

from ..dependencies.strapi import Strapi
from ..dependencies.supabase import SupabaseClient
from ..pipelines.containment import score_containment
from ..pipelines.embed import EmbeddingPipeline
from ..pipelines.keyphrases import suggest_keyphrases
from ..pipelines.nlp import nlp
from ..pipelines.profanity_filter import profanity_filter
from ..pipelines.summary import LongformerPipeline, SummaryPipeline
from ..schemas.strapi import Chunk
from ..schemas.summary import (
    ChunkWithWeight,
    Summary,
    SummaryInputStrapi,
    SummaryResults,
)
from ..services.summary_feedback import feedback_processors

content_pipe = LongformerPipeline("tiedaar/longformer-content-global")
language_pipe = SummaryPipeline("tiedaar/language-beyond-the-source")
embedding_pipe = EmbeddingPipeline()
detector = gcld3.NNetLanguageIdentifier(  # type: ignore
    min_num_bytes=0, max_num_bytes=1000
)


def weight_chunks(
    chunks: list[Chunk], chunk_docs: list[Doc], focus_time_dict: dict
) -> list[ChunkWithWeight]:
    """Weight chunks based on focus time"""
    weighted_chunks = []
    for chunk, chunk_doc in zip(chunks, chunk_docs):
        if not chunk.component_type == "page.chunk":
            continue
        focus_time = max(focus_time_dict.get(chunk.Slug, 1), 1)
        weight = 3.33 * (focus_time / len(chunk_doc))
        weighted_chunks.append(
            ChunkWithWeight(**chunk.model_dump(by_alias=True), weight=weight)
        )
    return weighted_chunks


async def summary_score(
    summary_input: SummaryInputStrapi,
    strapi: Strapi,
    supabase: SupabaseClient,
) -> tuple[Summary, SummaryResults]:
    """Checks summary for text copied from the source and for semantic
    relevance to the source text. If it passes these checks, score the summary
    using a Huggingface pipeline.
    """

    # Retrieve chunks from Strapi and weight them
    # 3.33 words per second is an average reading pace
    chunks = await strapi.get_chunks(summary_input.page_slug)

    chunk_docs = list(nlp.pipe([chunk.CleanText for chunk in chunks]))

    weighted_chunks = weight_chunks(chunks, chunk_docs, summary_input.focus_time)

    bot_messages = None
    if summary_input.chat_history:
        bot_messages = "\n".join(
            [msg.text for msg in summary_input.chat_history if msg.agent == "bot"]
        )

    # Create summary data object
    summary = Summary(
        summary=nlp(summary_input.summary),
        source=Doc.from_docs(chunk_docs),  # combine into a single doc
        chunks=weighted_chunks,
        page_slug=summary_input.page_slug,
        chat_history=summary_input.chat_history,
        bot_messages=nlp(bot_messages) if bot_messages else None,
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
    summary_embed = embedding_pipe(summary.summary.text)[0].tolist()
    results["similarity"] = (
        await supabase.page_similarity(summary_embed, summary.page_slug) + 0.15
    )  # adding 0.15 to bring similarity score in line with old doc2vec model

    # Generate keyphrase suggestions
    included, suggested = suggest_keyphrases(summary.summary, summary.chunks)
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
    junk_filter = any(
        score.feedback.is_passed is False
        for score in [
            feedback_processors["containment"](results["containment"]),
            feedback_processors["containment_chat"](
                results.get("containment_chat", 0.0)
            ),
            feedback_processors["similarity"](results["similarity"]),
            feedback_processors["english"](results["english"]),
            feedback_processors["profanity"](results["profanity"]),
        ]
    )

    if junk_filter:
        return summary, SummaryResults(**results)

    # Summary meets minimum requirements. Score it.
    input_text = summary.summary.text + "</s>" + summary.source.text
    results["content"] = float(content_pipe(input_text)[0]["score"])
    results["language"] = float(language_pipe(summary.summary.text)[0]["score"])

    return summary, SummaryResults(**results)

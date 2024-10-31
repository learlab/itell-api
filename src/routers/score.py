from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ..logging.logging_router import LoggingRoute, LoggingStreamingResponse
from ..schemas.answer import AnswerInputStrapi, AnswerResults
from ..schemas.chat import EventType
from ..schemas.summary import (
    StreamingSummaryResults,
    SummaryInputStrapi,
    SummaryResults,
    SummaryResultsWithFeedback,
)
from ..services.answer_eval import answer_score
from ..services.chat import language_feedback_chat
from ..services.stairs import sert_question
from ..services.summary_eval import summary_score
from ..services.summary_feedback import summary_feedback

router = APIRouter(route_class=LoggingRoute)


@router.post("/score/summary")
async def score_summary(
    input_body: SummaryInputStrapi,
    request: Request,
) -> SummaryResultsWithFeedback:
    """Score a summary.
    Requires a page_slug.
    """
    strapi = request.app.state.strapi
    supabase = request.app.state.supabase
    faiss = request.app.state.faiss
    _, results = await summary_score(input_body, strapi, supabase, faiss)
    feedback: SummaryResultsWithFeedback = summary_feedback(results)
    return feedback


@router.post("/score/answer")
async def score_answer(
    input_body: AnswerInputStrapi,
    request: Request,
) -> AnswerResults:
    """Score a constructed response item.
    Requires a page_slug and chunk_slug.
    """
    strapi = request.app.state.strapi
    return await answer_score(input_body, strapi)


@router.post("/score/summary/stairs", response_model=StreamingSummaryResults)
async def score_summary_with_stairs(
    input_body: SummaryInputStrapi,
    request: Request,
) -> StreamingResponse:
    """Scores a summary. If the summary fails, selects a chunk for re-reading and
    generates a self-explanation (SERT) question about the chunk.

    The response is a stream of Server-Sent Events (SSEs). The first response will
    be a SummaryResults object with additional fields for feedback.

    If the summary fails, subsequent responses will be:
    - **request_id**: a unique identifier for the request
    - **text**: the self-explanation question text
    - **chunk**: the slug of the chunk selected for re-reading
    - **question_type**: the type of SERT question
    """
    strapi = request.app.state.strapi
    supabase = request.app.state.supabase
    faiss = request.app.state.faiss
    summary, results = await summary_score(input_body, strapi, supabase, faiss)

    feedback: SummaryResultsWithFeedback = summary_feedback(results)

    feedback_stream = None

    # Failing specific scores triggers feedback as a token stream
    feedback_details = {item.type: item.feedback for item in feedback.prompt_details}

    if feedback_details["Content"].is_passed is False:
        feedback_stream = await sert_question(summary, strapi, faiss)
    elif feedback_details["Language"].is_passed is False:
        feedback_stream = await language_feedback_chat(summary, strapi)

    async def stream_results() -> AsyncGenerator[bytes, None]:
        event_str = f"event: {EventType.summary_feedback}"
        data_str = f"data: {feedback.model_dump_json()}\n\n"
        yield "\n".join([event_str, data_str]).encode("utf-8")
        if feedback_stream:
            async for chunk in feedback_stream:
                yield chunk

    return LoggingStreamingResponse(
        content=stream_results(), media_type="text/event-stream"
    )

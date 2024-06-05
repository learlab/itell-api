from ..models.summary import (
    SummaryInputStrapi,
    Summary,
    SummaryResults,
    StreamingSummaryResults,
    SummaryResultsWithFeedback,
)
from ..models.answer import AnswerInputStrapi, AnswerResults
from ..models.chat import EventType
from typing import AsyncGenerator

from ..answer_eval import answer_score
from ..summary_eval import summary_score
from ..summary_feedback import summary_feedback
from ..sert import sert_chat
from ..chat import language_feedback_chat

from .logging_router import LoggingRoute
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(route_class=LoggingRoute)


@router.post("/score/summary")
async def score_summary(input_body: SummaryInputStrapi) -> SummaryResults:
    """Score a summary.
    Requires a page_slug.
    """
    _, results = await summary_score(input_body)
    return results


@router.post("/score/answer")
async def score_answer(input_body: AnswerInputStrapi) -> AnswerResults:
    """Score a constructed response item.
    Requires a page_slug and chunk_slug.
    """
    return await answer_score(input_body)


@router.post("/score/summary/stairs", response_model=StreamingSummaryResults)
async def score_summary_with_stairs(
    input_body: SummaryInputStrapi,
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
    scoring_results: tuple[Summary, SummaryResults] = await summary_score(input_body)
    summary, results = scoring_results
    feedback: SummaryResultsWithFeedback = summary_feedback(results)

    feedback_stream = None

    # Failing specific scores triggers feedback as a token stream
    feedback_details = {item.type: item.feedback for item in feedback.prompt_details}

    if not feedback_details["Content"].is_passed:
        feedback_stream = await sert_chat(summary)
    elif not feedback_details["Language"].is_passed:
        feedback_stream = await language_feedback_chat(summary)

    async def stream_results() -> AsyncGenerator[bytes, None]:
        event_str = f"event: {EventType.summary_feedback}"
        data_str = f"data: {feedback.model_dump_json()}\n\n"
        yield "\n".join([event_str, data_str]).encode("utf-8")
        if feedback_stream:
            async for chunk in feedback_stream:
                yield chunk

    return StreamingResponse(content=stream_results(), media_type="text/event-stream")

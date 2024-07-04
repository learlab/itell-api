import json
import logging
import time
from typing import Callable

from fastapi import BackgroundTasks, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask

from ..models.logging import LogEntry
from .logging_streaming_response import LoggingStreamingResponse

logger = logging.getLogger("itell_ai")


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # This start time measurement is appropriate for all responses
            start_time = time.perf_counter()
            await request.body()
            response = await original_route_handler(request)

            if isinstance(response, StreamingResponse):
                response.start_time = start_time
            else:
                # Only appropriate for non-streaming responses
                response.process_time = time.perf_counter() - start_time

            tasks = [BackgroundTask(self.log, request, response)]

            # Put any existing task first
            if response.background:
                tasks = [response.background, *tasks]
            response.background = BackgroundTasks(tasks=tasks)

            return response

        return custom_route_handler

    async def log(self, request: Request, response: Response) -> None:
        response_body = {}
        if isinstance(response, LoggingStreamingResponse):
            # Wait for the stream to finish
            await response.wait_for_completion()

            # Log first chunk for STAIRS endpoint
            if request.url.path == "/score/summary/stairs":
                response_body.update(response.first_message)

            # Log last chunk for all endpoints if it exists
            # Will not exist for passing summaries at /score/summary/stairs
            if response.last_message:
                response_body.update(response.last_message)

        elif response.body:
            response_body = json.loads(response.body)

        log_entry = LogEntry(
            api_endpoint=request.url.path,
            request_method=request.method,
            request_body=await request.json(),
            response_body=response_body,
            status_code=response.status_code,
            client_address=request.client.host,
            process_time=response.process_time,
            ttft=response.ttft if hasattr(response, "ttft") else None,
        )

        logger("Request Processed", extra=log_entry.model_dump())

        # Log to Supabase
        # await request.app.state.supabase.table("logs").insert(log_entry)

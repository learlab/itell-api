import asyncio
import json
import logging
import os
import time
from typing import AsyncIterator, Callable

from fastapi import BackgroundTasks, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask

from ..models.logging import LogEntry


class LoggingStreamingResponse(StreamingResponse):
    """A starlette.StreamingResponse Wrapper
    - Stores the first and last chunk of the stream.
    - Method to parse SSE event chunks as JSON
    - Performance timing for time-to-first-token and total processing time
    - Awaitable event to ensure the stream is finished before logging
    """

    def __init__(self, content: AsyncIterator, *args, **kwargs):
        super().__init__(self.wrap_content(content), *args, **kwargs)
        self._is_done = asyncio.Event()

    async def wrap_content(self, content: AsyncIterator):
        self._first_chunk = await content.__anext__()
        yield self._first_chunk

        # Time to first token (ttft)
        # For /score/summary/stairs, represents time to summary feedback
        # Since summary feedback is the first chunk
        self.ttft = time.perf_counter() - self.start_time

        self._last_chunk = None
        async for chunk in content:
            self._last_chunk = chunk
            yield chunk

        # Do not record ttft if stream is one chunk long
        # Happens when STAIRS is not triggered on /score/summary/stairs
        if self._last_chunk is None:
            self.ttft = None

        self.process_time = time.perf_counter() - self.start_time
        self._is_done.set()

    def parse_sse(self, chunk: str | bytes) -> str:
        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8")

        # get content after "\ndata: "
        try:
            return json.loads(chunk.split("\ndata: ")[1].strip())
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            logging.error(f"Failed to parse SSE chunk: {chunk}. Error: {e}")

    @property
    def first_message(self):
        return self.parse_sse(self._first_chunk)

    @property
    def last_message(self):
        if self._last_chunk:
            return self.parse_sse(self._last_chunk)

    async def wait_for_completion(self):
        await self._is_done.wait()


class LoggingRoute(APIRoute):
    log_to_stdout = True
    log_to_db = True  # os.getenv("ENV") == "production"

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

            tasks = [BackgroundTask(self.log_all, request, response)]

            # Put any existing task first
            if response.background:
                tasks = [response.background, *tasks]
            response.background = BackgroundTasks(tasks=tasks)

            return response

        return custom_route_handler

    async def log_all(self, request: Request, response: Response) -> None:
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

        if self._log_to_stdout:
            self._log_to_stdout(log_entry)
        if self.log_to_db:
            await self._log_to_db(log_entry)

    def _log_to_stdout(self, log_entry: LogEntry) -> None:
        logging.info(log_entry)

    async def _log_to_db(self, log_entry: LogEntry) -> None:
        print(log_entry.api_endpoint, log_entry.ttft, log_entry.process_time)
        # await request.app.state.supabase.table("logs").insert(payload).execute()

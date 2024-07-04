import asyncio
import json
import logging
import time
import uuid
from typing import AsyncIterator, Callable

from fastapi import BackgroundTasks, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask


class LoggingStreamingResponse(StreamingResponse):
    """A StreamingResponse that stores the first and last chunk of the stream.
    Also includes a performance timer and
    methods to access the first and last messages of the stream as dicts
    """

    def __init__(self, content: AsyncIterator, *args, **kwargs):
        super().__init__(self.wrap_content(content), *args, **kwargs)
        self._is_done = asyncio.Event()

    async def wrap_content(self, content: AsyncIterator):
        self._first_chunk = await content.__anext__()
        yield self._first_chunk

        # Time to first token
        self.ttft = time.perf_counter() - self.start_time

        self._last_chunk = None
        async for chunk in content:
            self._last_chunk = chunk
            yield chunk

        self._is_done.set()

        # Full process time
        self.process_time = time.perf_counter() - self.start_time

    def parse_sse(self, chunk: str | bytes) -> str:
        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8")

        # get content after "\ndata: "
        try:
            return json.loads(chunk.split("\ndata: ")[1])
        except (IndexError, TypeError, json.JSONDecodeError) as e:
            logging.error(f"Failed to parse SSE chunk: {chunk}. Error: {e}")

    @property
    def first_message(self):
        return self.parse_sse(self._first_chunk)

    @property
    def last_message(self):
        if self._last_chunk:
            return self.parse_sse(self._last_chunk)

    async def wait_for_completion(self):
        # Wait for the last chunk to be generated before logging
        await self._is_done.wait()


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start_time = time.perf_counter()
            req_body = await request.body()
            response = await original_route_handler(request)
            existing_task = response.background
            process_time = time.perf_counter() - start_time

            if isinstance(response, StreamingResponse):
                response_body = None
                # For streaming responses, the end time is calculated
                # when the stream is finished, not here.
                response.start_time = start_time
            else:
                response_body = response.body.decode()
                # Add processing time to response if not a streaming response
                response.process_time = process_time

            file_log = BackgroundTask(self.file_log, req_body.decode(), response_body)
            db_log = BackgroundTask(self.db_log, request, response)
            tasks = [file_log, db_log]

            # Put any existing tasks first
            if existing_task:
                tasks = [existing_task, *tasks]
            response.background = BackgroundTasks(tasks=tasks)

            return response

        return custom_route_handler

    def file_log(self, req: str, resp: str | None) -> None:
        idem = str(uuid.uuid4())
        logging.info(f"REQUEST  {idem}: {req}")
        if resp:
            logging.info(f"RESPONSE {idem}: {resp}")

    async def db_log(self, request: Request, response: Response) -> None:
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
            else:
                # Do not record ttft if STAIRS was not triggered
                response.ttft = None

        elif response.body:
            response_body = response.body

        payload = {
            "api_endpoint": request.url.path,
            "request_method": request.method,
            "request_body": await request.json(),
            "response_body": response_body,
            "status_code": response.status_code,
            "ip_address": request.client.host,
            "process_time": response.process_time,
            "ttft": response.ttft if hasattr(response, "ttft") else None,
        }

        print(payload["api_endpoint"], payload["ttft"], payload["process_time"])
        # await request.app.state.supabase.table("logs").insert(payload).execute()

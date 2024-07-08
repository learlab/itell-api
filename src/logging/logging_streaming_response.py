import asyncio
import json
import logging
import time
from typing import AsyncIterator

from fastapi.responses import StreamingResponse


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

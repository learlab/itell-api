
from fastapi.routing import APIRoute
from fastapi import Request, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from typing import Callable

import uuid
import logging


def log_info(req: str, resp: str) -> None:
    idem = str(uuid.uuid4())
    logging.info(f"REQUEST  {idem}: {req}")
    logging.info(f"RESPONSE {idem}: {resp}")


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()
            response = await original_route_handler(request)
            existing_task = response.background

            if isinstance(response, StreamingResponse):
                task = BackgroundTask(
                    log_info, req_body.decode(), "streaming response")
            else:
                task = BackgroundTask(
                    log_info, req_body.decode(), response.body.decode()
                )

            # check if the original response had a background task assigned to it
            if existing_task:
                response.background = BackgroundTasks(
                    tasks=[existing_task, task])
            else:
                response.background = task

            return response

        return custom_route_handler

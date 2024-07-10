from typing import Optional

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    api_endpoint: str
    request_method: str
    request_body: dict
    response_body: Optional[dict]
    status_code: int
    client_name: str
    process_time: float
    ttft: Optional[float] = Field(
        None,
        description=(
            "Time to first token. For /score/summary/stairs,"
            " represents time to summary feedback.",
        ),
    )

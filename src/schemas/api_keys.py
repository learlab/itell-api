from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateAPIKeyInput(BaseModel):
    nickname: str
    role: str


class DeleteAPIKeyInput(BaseModel):
    api_key: str


class AuthEntry(BaseModel):
    created_at: Optional[datetime] = None
    api_key: Optional[str] = None
    role: str
    nickname: str

from pydantic import BaseModel


class CreateAPIKeyInput(BaseModel):
    nickname: str
    role: str


class DeleteAPIKeyInput(BaseModel):
    api_key: str

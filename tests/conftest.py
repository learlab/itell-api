import os

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from src.schemas.chat import ChatResponse


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def app():
    from src.app import get_app

    app = get_app()

    async with LifespanManager(app) as manager:
        yield manager.app


@pytest.fixture(scope="session", autouse=True)
async def client(anyio_backend, app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"API-Key": os.environ["ITELL_API_KEY"]},
    ) as client:
        yield client


@pytest.fixture
async def supabase():
    url: str = os.environ["VECTOR_HOST"]
    key: str = os.environ["VECTOR_KEY"]
    from src.dependencies.supabase import SupabaseClient

    yield SupabaseClient(url, key)


@pytest.fixture(scope="session")
def parser():
    def parser(response_text):
        response_text = response_text.split("\ndata: ")[-1].strip()
        last_message = ChatResponse.model_validate_json(response_text).text
        return last_message.strip()

    return parser

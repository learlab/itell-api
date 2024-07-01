import os

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def app():
    from src.app import app

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

import pytest
from httpx import AsyncClient


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def client(anyio_backend):
    from src.main import app

    client = AsyncClient(app=app, base_url="http://test")
    yield client
    await client.aclose()

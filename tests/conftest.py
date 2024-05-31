from httpx import AsyncClient
import os
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def client(anyio_backend):
    from src.main import app

    client = AsyncClient(
        app=app,
        base_url="http://test",
        headers={"API-Key": os.environ["ITELL_API_KEY"]}
    )
    yield client
    await client.aclose()


@pytest.fixture(scope="module")
async def db():
    from src.connections.vectorstore import get_vector_store

    db = get_vector_store()
    yield db

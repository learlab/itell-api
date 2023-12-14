import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def client():
    from src.main import app

    return TestClient(app)

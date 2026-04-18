"""Shared fixtures for all tests."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.store import reset_store


@pytest.fixture(autouse=True)
def clear_store():
    """Reset the in-memory store before each test."""
    reset_store()
    yield
    reset_store()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

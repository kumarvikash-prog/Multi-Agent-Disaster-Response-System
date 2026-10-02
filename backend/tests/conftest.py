"""Test configuration and shared fixtures for the backend test suite.

Tests that require a real database use the ``TEST_DATABASE_URL`` env var.
Tests that do NOT need a database (the majority) use the FastAPI TestClient
with a mocked ``get_session`` dependency.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure tests use the test database, never the dev one
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://localhost/disasterai_test"),
)
os.environ.setdefault("JWT_SECRET", "test-secret-32-chars-long-for-tests")
os.environ.setdefault("ENV", "test")


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Return the FastAPI application (created once per test session)."""
    from app.main import create_app

    return create_app()


@pytest.fixture(scope="session")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Return a TestClient that does NOT start a real server."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

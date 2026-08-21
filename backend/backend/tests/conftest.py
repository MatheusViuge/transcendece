import os
from pathlib import Path

# Configuration must exist before application modules are imported during test collection.
TEST_DB_PATH = Path("/tmp/transcendece_backend_tests.sqlite3")
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH}"
os.environ["JWT_SECRET_KEY"] = "test-only-jwt-secret-that-is-long-enough-123456"

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 - register all SQLAlchemy tables before create_all
from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_test_database():
    """Give every integration test a deterministic disposable database."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client

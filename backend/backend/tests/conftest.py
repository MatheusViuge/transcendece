import os
import shutil
from pathlib import Path

# Configuration must exist before application modules are imported during test collection.
TEST_DB_PATH = Path("/tmp/transcendece_backend_tests.sqlite3")
TEST_STORAGE_PATH = Path("/tmp/transcendece_file_upload_tests")
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH}"
os.environ["JWT_SECRET_KEY"] = "test-only-jwt-secret-that-is-long-enough-123456"
os.environ["FILE_STORAGE_ROOT"] = str(TEST_STORAGE_PATH)

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401 - register all SQLAlchemy tables before create_all
from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_test_database():
    """Give every integration test a deterministic disposable database/storage."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    shutil.rmtree(TEST_STORAGE_PATH, ignore_errors=True)
    TEST_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    shutil.rmtree(TEST_STORAGE_PATH, ignore_errors=True)


@pytest.fixture()
def client():
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client

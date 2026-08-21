from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from jose import jwt
from starlette.requests import Request

from app.core.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.core.middleware import _is_public_request
from app.core.security import allowed_roles, create_access_token, verify_token


class FakeQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.user


class FakeDb:
    def __init__(self, user):
        self.user = user

    def query(self, _model):
        return FakeQuery(self.user)


def make_request(path: str = "/protected", method: str = "GET") -> Request:
    return Request(
        {
            "type": "http",
            "method": method,
            "path": path,
            "raw_path": path.encode(),
            "root_path": "",
            "scheme": "https",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("localhost", 443),
        }
    )


def test_access_token_round_trip_has_minimum_claims():
    token = create_access_token(42, "USER@EXAMPLE.COM", "admin")
    payload = verify_token(token)

    assert payload["id"] == 42
    assert payload["email"] == "user@example.com"
    assert payload["iat"] is not None
    assert payload["exp"] is not None
    assert "role" not in payload


def test_expired_token_is_rejected():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "42",
            "email": "user@example.com",
            "type": "access",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)

    assert exc_info.value.status_code == 401


def test_token_signed_with_another_secret_is_rejected():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "42",
            "email": "user@example.com",
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        "different-secret-that-is-also-long-enough-123",
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)

    assert exc_info.value.status_code == 401


def test_token_without_access_type_is_rejected():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "42",
            "email": "user@example.com",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(HTTPException):
        verify_token(token)


def test_allowed_roles_uses_current_database_role():
    request = make_request()
    request.state.user = {"id": 42, "email": "user@example.com"}
    db_user = SimpleNamespace(id=42, email="user@example.com", tipo_usuario="admin")

    dependency = allowed_roles("admin")
    result = dependency(request, FakeDb(db_user))

    assert result == {"id": 42, "email": "user@example.com", "role": "admin"}


def test_role_denied_returns_403_not_401():
    request = make_request()
    request.state.user = {"id": 42, "email": "user@example.com"}
    db_user = SimpleNamespace(id=42, email="user@example.com", tipo_usuario="aluno")

    dependency = allowed_roles("admin")
    with pytest.raises(HTTPException) as exc_info:
        dependency(request, FakeDb(db_user))

    assert exc_info.value.status_code == 403


def test_missing_database_user_invalidates_session():
    request = make_request()
    request.state.user = {"id": 42, "email": "user@example.com"}

    dependency = allowed_roles()
    with pytest.raises(HTTPException) as exc_info:
        dependency(request, FakeDb(None))

    assert exc_info.value.status_code == 401


def test_health_and_cors_preflight_are_public():
    health = make_request("/status")
    preflight = make_request("/anything", method="OPTIONS")

    assert _is_public_request(health, "/status") is True
    assert _is_public_request(preflight, "/anything") is True


def test_unknown_role_configuration_fails_fast():
    with pytest.raises(ValueError):
        allowed_roles("superadmin")

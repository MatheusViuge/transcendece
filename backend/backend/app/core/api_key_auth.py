from __future__ import annotations

import hashlib
import hmac
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.security import ALLOWED_ROLES
from app.database import get_db
from app.models.api_key import ApiKey
from app.models.user import Usuario
from app.services.api_key_service import deserialize_scopes

PUBLIC_API_RATE_LIMIT = int(os.getenv("PUBLIC_API_RATE_LIMIT", "20"))
PUBLIC_API_RATE_WINDOW_SECONDS = int(os.getenv("PUBLIC_API_RATE_WINDOW_SECONDS", "60"))

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API key emitida por um usuário autenticado. O secret completo só é exibido na criação/rotação.",
)


@dataclass(frozen=True)
class ApiKeyContext:
    key_id: int
    owner_id: int
    owner_role: str
    scopes: frozenset[str]
    rate_headers: dict[str, str]


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _extract_prefix(secret: str) -> str | None:
    parts = secret.split("_", 2)
    if len(parts) != 3 or parts[0] != "ic" or len(parts[1]) != 8:
        return None
    return f"ic_{parts[1]}"


def _hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key ausente, inválida ou revogada.",
        headers={"WWW-Authenticate": "ApiKey"},
    )


def authenticate_api_key(
    raw_key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> ApiKeyContext:
    if not raw_key:
        raise _auth_error()

    prefix = _extract_prefix(raw_key.strip())
    if prefix is None:
        raise _auth_error()

    api_key = (
        db.query(ApiKey)
        .filter(ApiKey.prefix == prefix)
        .with_for_update()
        .first()
    )
    if api_key is None or api_key.revoked_at is not None:
        db.rollback()
        raise _auth_error()

    candidate_hash = _hash_secret(raw_key.strip())
    if not hmac.compare_digest(candidate_hash, api_key.key_hash):
        db.rollback()
        raise _auth_error()

    owner = db.query(Usuario).filter(Usuario.id == api_key.owner_id).first()
    if owner is None or not owner.is_active or owner.tipo_usuario not in ALLOWED_ROLES:
        db.rollback()
        raise _auth_error()

    now = datetime.now(timezone.utc)
    window_start = _utc(api_key.rate_window_started_at) if api_key.rate_window_started_at else now
    elapsed = (now - window_start).total_seconds()

    if api_key.rate_window_started_at is None or elapsed >= PUBLIC_API_RATE_WINDOW_SECONDS:
        window_start = now
        api_key.rate_window_started_at = now
        api_key.rate_request_count = 0

    reset_at = window_start + timedelta(seconds=PUBLIC_API_RATE_WINDOW_SECONDS)
    if api_key.rate_request_count >= PUBLIC_API_RATE_LIMIT:
        retry_after = max(1, math.ceil((reset_at - now).total_seconds()))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit da API key excedido.",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(PUBLIC_API_RATE_LIMIT),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_at.timestamp())),
            },
        )

    api_key.rate_request_count += 1
    api_key.last_used_at = now
    remaining = max(0, PUBLIC_API_RATE_LIMIT - api_key.rate_request_count)
    db.commit()

    return ApiKeyContext(
        key_id=api_key.id,
        owner_id=owner.id,
        owner_role=owner.tipo_usuario,
        scopes=frozenset(deserialize_scopes(api_key.scopes)),
        rate_headers={
            "X-RateLimit-Limit": str(PUBLIC_API_RATE_LIMIT),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(reset_at.timestamp())),
        },
    )


def require_api_key(*required_scopes: str):
    def dependency(context: ApiKeyContext = Depends(authenticate_api_key)) -> ApiKeyContext:
        if not set(required_scopes).issubset(context.scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key não possui os scopes exigidos para esta operação.",
            )
        return context

    return dependency

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.api_key import ApiKey
from app.models.user import Usuario

ALLOWED_API_KEY_SCOPES = {"courses:read", "courses:write"}
READ_SCOPE = "courses:read"
WRITE_SCOPE = "courses:write"


def _hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _serialize_scopes(scopes: set[str]) -> str:
    return ",".join(sorted(scopes))


def deserialize_scopes(value: str) -> set[str]:
    return {scope for scope in value.split(",") if scope}


def default_scopes_for(user: Usuario) -> set[str]:
    if user.tipo_usuario == "instrutor":
        return {READ_SCOPE, WRITE_SCOPE}
    return {READ_SCOPE}


def validate_scopes(user: Usuario, requested: list[str] | None) -> set[str]:
    scopes = set(requested) if requested is not None else default_scopes_for(user)
    if not scopes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ao menos um scope é obrigatório.")
    unknown = scopes - ALLOWED_API_KEY_SCOPES
    if unknown:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Scope de API key inválido.")
    if WRITE_SCOPE in scopes and user.tipo_usuario != "instrutor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente instrutores podem emitir API keys com permissão de escrita.",
        )
    return scopes


def _new_secret(db: Session) -> tuple[str, str, str]:
    for _ in range(10):
        prefix = f"ic_{secrets.token_hex(4)}"
        if db.query(ApiKey.id).filter(ApiKey.prefix == prefix).first() is None:
            secret = f"{prefix}_{secrets.token_urlsafe(32)}"
            return secret, prefix, _hash_secret(secret)
    raise RuntimeError("Não foi possível gerar um prefixo único para API key.")


def issue_api_key(
    db: Session,
    *,
    owner: Usuario,
    name: str,
    requested_scopes: list[str] | None,
) -> tuple[ApiKey, str]:
    scopes = validate_scopes(owner, requested_scopes)
    secret, prefix, key_hash = _new_secret(db)
    api_key = ApiKey(
        owner_id=owner.id,
        name=name.strip(),
        prefix=prefix,
        key_hash=key_hash,
        scopes=_serialize_scopes(scopes),
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, secret


def list_api_keys(db: Session, *, owner_id: int) -> list[ApiKey]:
    return (
        db.query(ApiKey)
        .filter(ApiKey.owner_id == owner_id)
        .order_by(ApiKey.created_at.desc(), ApiKey.id.desc())
        .all()
    )


def get_owned_api_key(db: Session, *, owner_id: int, api_key_id: int) -> ApiKey:
    api_key = (
        db.query(ApiKey)
        .filter(ApiKey.id == api_key_id, ApiKey.owner_id == owner_id)
        .first()
    )
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key não encontrada.")
    return api_key


def revoke_api_key(db: Session, *, owner_id: int, api_key_id: int) -> ApiKey:
    api_key = get_owned_api_key(db, owner_id=owner_id, api_key_id=api_key_id)
    if api_key.revoked_at is None:
        api_key.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(api_key)
    return api_key


def rotate_api_key(db: Session, *, owner: Usuario, api_key_id: int) -> tuple[ApiKey, str]:
    current = get_owned_api_key(db, owner_id=owner.id, api_key_id=api_key_id)
    if current.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="API key já revogada.")
    current.revoked_at = datetime.now(timezone.utc)
    db.flush()

    secret, prefix, key_hash = _new_secret(db)
    replacement = ApiKey(
        owner_id=owner.id,
        name=current.name,
        prefix=prefix,
        key_hash=key_hash,
        scopes=current.scopes,
    )
    db.add(replacement)
    db.commit()
    db.refresh(replacement)
    return replacement, secret

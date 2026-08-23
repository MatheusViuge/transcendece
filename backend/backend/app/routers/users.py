from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import get_db
from app.models.friendship import Friendship
from app.models.uploaded_file import UploadedFile
from app.models.user import Usuario
from app.schemas.user import UsuarioAtualizarParcial
from app.services.file_storage import remove_stored_file, stored_path

router = APIRouter(prefix="/users", tags=["User Management"])
PRESENCE_TTL = timedelta(seconds=90)
DEFAULT_AVATAR_URL = "/default-avatar.svg"
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


def _get_active_user(db: Session, user_id: int) -> Usuario:
    user = db.query(Usuario).filter(Usuario.id == user_id, Usuario.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return user


def _normalized(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _is_online(user: Usuario) -> bool:
    last_seen = _normalized(user.last_seen_at)
    return last_seen is not None and datetime.now(timezone.utc) - last_seen <= PRESENCE_TTL


def _avatar_url(user: Usuario) -> str:
    return DEFAULT_AVATAR_URL if user.avatar_file_id is None else f"/api/users/{user.id}/avatar"


def _public_payload(user: Usuario) -> dict[str, object]:
    return {
        "id": user.id,
        "nome": user.nome,
        "sobrenome": user.sobrenome,
        "tipo_usuario": user.tipo_usuario,
        "data_cadastro": user.data_cadastro,
        "avatar_url": _avatar_url(user),
        "online": _is_online(user),
    }


def _private_payload(user: Usuario) -> dict[str, object]:
    return {
        **_public_payload(user),
        "email": user.email,
        "data_nascimento": user.data_nascimento,
        "ultimo_login": user.ultimo_login,
        "ultima_atualizacao": user.ultima_atualizacao,
    }


def _pair(first_id: int, second_id: int) -> tuple[int, int]:
    return (first_id, second_id) if first_id < second_id else (second_id, first_id)


def _friendship_query(db: Session, user_id: int):
    return db.query(Friendship).filter(or_(Friendship.user_low_id == user_id, Friendship.user_high_id == user_id))


@router.get("/me")
def get_own_profile(db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    user = _get_active_user(db, identity["id"])
    user.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return success_response(data=_private_payload(user), message="Perfil retornado com sucesso.")


@router.patch("/me")
def update_own_profile(payload: UsuarioAtualizarParcial, db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    user = _get_active_user(db, identity["id"])
    changes = payload.model_dump(exclude_unset=True)
    if "email" in changes:
        email = str(changes["email"]).strip().lower()
        conflict = db.query(Usuario).filter(Usuario.email == email, Usuario.id != user.id).first()
        if conflict is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado.")
        changes["email"] = email
    for field, value in changes.items():
        setattr(user, field, value)
    user.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return success_response(data=_private_payload(user), message="Perfil atualizado com sucesso.")


@router.post("/presence/heartbeat")
def heartbeat(db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    user = _get_active_user(db, identity["id"])
    user.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    return success_response(data={"online": True, "ttl_seconds": int(PRESENCE_TTL.total_seconds())}, message="Presença atualizada.")


@router.get("/friends")
def list_friends(db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    own_id = identity["id"]
    rows = _friendship_query(db, own_id).order_by(Friendship.created_at.asc()).all()
    friend_ids = [row.user_high_id if row.user_low_id == own_id else row.user_low_id for row in rows]
    if not friend_ids:
        return success_response(data=[], message="Amigos retornados com sucesso.")
    users = db.query(Usuario).filter(Usuario.id.in_(friend_ids), Usuario.is_active.is_(True)).all()
    by_id = {user.id: user for user in users}
    return success_response(data=[_public_payload(by_id[item]) for item in friend_ids if item in by_id], message="Amigos retornados com sucesso.")


@router.post("/friends/{user_id}", status_code=status.HTTP_201_CREATED)
def add_friend(user_id: int, db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    own_id = identity["id"]
    if own_id == user_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Você não pode adicionar a si mesmo como amigo.")
    friend = _get_active_user(db, user_id)
    low_id, high_id = _pair(own_id, user_id)
    if db.query(Friendship).filter(Friendship.user_low_id == low_id, Friendship.user_high_id == high_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já está na sua lista de amigos.")
    try:
        db.add(Friendship(user_low_id=low_id, user_high_id=high_id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Amizade já existe.")
    return success_response(data=_public_payload(friend), message="Amigo adicionado com sucesso.", status_code=status.HTTP_201_CREATED)


@router.delete("/friends/{user_id}")
def remove_friend(user_id: int, db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    low_id, high_id = _pair(identity["id"], user_id)
    relation = db.query(Friendship).filter(Friendship.user_low_id == low_id, Friendship.user_high_id == high_id).first()
    if relation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amizade não encontrada.")
    db.delete(relation)
    db.commit()
    return success_response(data={"id": user_id}, message="Amigo removido com sucesso.")


@router.put("/me/avatar/{file_id}")
def set_avatar(file_id: int, db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    user = _get_active_user(db, identity["id"])
    item = db.query(UploadedFile).filter(UploadedFile.id == file_id, UploadedFile.owner_id == user.id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo de avatar não encontrado.")
    if item.content_type not in IMAGE_TYPES or item.purpose != "avatar":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Avatar deve ser PNG, JPEG ou WebP enviado com purpose=avatar.")
    old_id = user.avatar_file_id
    user.avatar_file_id = item.id
    user.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    if old_id is not None and old_id != item.id:
        old = db.query(UploadedFile).filter(UploadedFile.id == old_id, UploadedFile.owner_id == user.id).first()
        if old is not None:
            storage_name = old.storage_name
            db.delete(old)
            db.commit()
            remove_stored_file(storage_name)
    return success_response(data=_private_payload(user), message="Avatar atualizado com sucesso.")


@router.delete("/me/avatar")
def remove_avatar(db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    user = _get_active_user(db, identity["id"])
    old_id = user.avatar_file_id
    user.avatar_file_id = None
    db.commit()
    if old_id is not None:
        old = db.query(UploadedFile).filter(UploadedFile.id == old_id, UploadedFile.owner_id == user.id).first()
        if old is not None:
            storage_name = old.storage_name
            db.delete(old)
            db.commit()
            remove_stored_file(storage_name)
    db.refresh(user)
    return success_response(data=_private_payload(user), message="Avatar removido; avatar padrão restaurado.")


@router.get("/{user_id}/avatar")
def get_avatar(user_id: int, db: Session = Depends(get_db)):
    """Serve somente o avatar explicitamente escolhido para o perfil público."""
    user = _get_active_user(db, user_id)
    if user.avatar_file_id is None:
        return RedirectResponse(url=DEFAULT_AVATAR_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    item = db.query(UploadedFile).filter(UploadedFile.id == user.avatar_file_id, UploadedFile.owner_id == user.id).first()
    if item is None or item.content_type not in IMAGE_TYPES:
        return RedirectResponse(url=DEFAULT_AVATAR_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    path = stored_path(item.storage_name)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Avatar físico não está disponível.")
    encoded_name = quote(Path(item.original_name).name, safe="")
    return FileResponse(path=path, media_type=item.content_type, headers={"Content-Disposition": f"inline; filename*=UTF-8''{encoded_name}", "X-Content-Type-Options": "nosniff", "Cache-Control": "public, max-age=60"})


@router.get("")
def search_users(q: str = Query(default="", max_length=80), limit: int = Query(default=20, ge=1, le=50), db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    query = db.query(Usuario).filter(Usuario.is_active.is_(True), Usuario.id != identity["id"])
    term = q.strip()
    if term:
        pattern = f"%{term}%"
        query = query.filter(or_(Usuario.nome.ilike(pattern), Usuario.sobrenome.ilike(pattern), Usuario.email.ilike(pattern)))
    users = query.order_by(Usuario.nome.asc(), Usuario.sobrenome.asc()).limit(limit).all()
    return success_response(data=[_public_payload(user) for user in users], message="Usuários retornados com sucesso.")


@router.get("/{user_id}")
def get_public_profile(user_id: int, db: Session = Depends(get_db), identity=Depends(allowed_roles())):
    del identity
    return success_response(data=_public_payload(_get_active_user(db, user_id)), message="Perfil público retornado com sucesso.")

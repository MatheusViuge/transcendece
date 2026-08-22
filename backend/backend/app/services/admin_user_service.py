from __future__ import annotations

import logging
import math
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.instructor import Instrutor
from app.models.specialty import Especialidade
from app.models.user import Usuario
from app.schemas.admin import AdminUserCreate, AdminUserUpdate
from app.services.auth_service import get_password_hash

logger = logging.getLogger(__name__)
VALID_ROLES = {"aluno", "instrutor", "admin"}


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _active_admin_count(db: Session) -> int:
    return (
        db.query(Usuario)
        .filter(Usuario.tipo_usuario == "admin", Usuario.is_active.is_(True))
        .count()
    )


def _ensure_specialty(db: Session, specialty_id: int | None) -> Especialidade:
    if specialty_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="especialidade_id é obrigatório para a role instrutor.",
        )
    specialty = db.query(Especialidade).filter(Especialidade.id == specialty_id).first()
    if specialty is None:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada.")
    return specialty


def list_users(
    db: Session,
    *,
    page: int,
    page_size: int,
    query: str | None,
    role: str | None,
    active: bool | None,
) -> tuple[list[Usuario], int, int]:
    users = db.query(Usuario)
    if query:
        needle = f"%{query.strip()}%"
        users = users.filter(
            or_(
                Usuario.nome.ilike(needle),
                Usuario.sobrenome.ilike(needle),
                Usuario.email.ilike(needle),
            )
        )
    if role:
        users = users.filter(Usuario.tipo_usuario == role)
    if active is not None:
        users = users.filter(Usuario.is_active.is_(active))

    total = users.count()
    total_pages = math.ceil(total / page_size) if total else 0
    items = (
        users.order_by(Usuario.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total, total_pages


def create_user(db: Session, *, payload: AdminUserCreate, actor_id: int) -> Usuario:
    email = _normalize_email(str(payload.email))
    if db.query(Usuario.id).filter(Usuario.email == email).first() is not None:
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    if payload.role == "instrutor":
        _ensure_specialty(db, payload.especialidade_id)

    user = Usuario(
        nome=payload.nome.strip(),
        sobrenome=payload.sobrenome.strip(),
        email=email,
        senha_hash=get_password_hash(payload.senha),
        data_nascimento=payload.data_nascimento,
        tipo_usuario=payload.role,
        is_active=True,
    )
    db.add(user)
    db.flush()

    if payload.role == "instrutor":
        db.add(
            Instrutor(
                id=user.id,
                especialidade=payload.especialidade_id,
                biografia=None,
            )
        )

    db.commit()
    db.refresh(user)
    logger.info("admin_user_created actor_id=%s target_id=%s role=%s", actor_id, user.id, user.tipo_usuario)
    return user


def update_user(
    db: Session,
    *,
    target: Usuario,
    payload: AdminUserUpdate,
    actor_id: int,
) -> Usuario:
    values = payload.model_dump(exclude_none=True)
    if "email" in values:
        email = _normalize_email(str(values["email"]))
        conflict = (
            db.query(Usuario.id)
            .filter(Usuario.email == email, Usuario.id != target.id)
            .first()
        )
        if conflict is not None:
            raise HTTPException(status_code=409, detail="Email já cadastrado.")
        values["email"] = email

    for field, value in values.items():
        setattr(target, field, value.strip() if isinstance(value, str) else value)

    db.commit()
    db.refresh(target)
    logger.info("admin_user_updated actor_id=%s target_id=%s", actor_id, target.id)
    return target


def change_role(
    db: Session,
    *,
    target: Usuario,
    new_role: str,
    specialty_id: int | None,
    actor_id: int,
) -> Usuario:
    if new_role not in VALID_ROLES:
        raise HTTPException(status_code=422, detail="Role inválida.")
    if target.id == actor_id and new_role != target.tipo_usuario:
        raise HTTPException(status_code=409, detail="Administrador não pode alterar a própria role.")

    old_role = target.tipo_usuario
    if old_role == "admin" and new_role != "admin" and target.is_active and _active_admin_count(db) <= 1:
        raise HTTPException(status_code=409, detail="Não é permitido remover o último administrador ativo.")

    instructor = target.instrutor
    if old_role == "instrutor" and new_role != "instrutor" and instructor is not None:
        if instructor.cursos:
            raise HTTPException(
                status_code=409,
                detail="Instrutor com cursos não pode mudar de role antes de transferir os cursos.",
            )
        db.delete(instructor)
        db.flush()

    if new_role == "instrutor":
        _ensure_specialty(db, specialty_id)
        if target.instrutor is None:
            db.add(Instrutor(id=target.id, especialidade=specialty_id, biografia=None))
        else:
            target.instrutor.especialidade = specialty_id

    target.tipo_usuario = new_role
    db.commit()
    db.refresh(target)
    logger.info(
        "admin_role_changed actor_id=%s target_id=%s old_role=%s new_role=%s",
        actor_id,
        target.id,
        old_role,
        new_role,
    )
    return target


def set_active_state(
    db: Session,
    *,
    target: Usuario,
    is_active: bool,
    actor_id: int,
) -> Usuario:
    if target.id == actor_id and not is_active:
        raise HTTPException(status_code=409, detail="Administrador não pode desativar a própria conta.")
    if target.tipo_usuario == "admin" and target.is_active and not is_active and _active_admin_count(db) <= 1:
        raise HTTPException(status_code=409, detail="Não é permitido desativar o último administrador ativo.")

    target.is_active = is_active
    db.commit()
    db.refresh(target)
    logger.info(
        "admin_user_status_changed actor_id=%s target_id=%s active=%s",
        actor_id,
        target.id,
        is_active,
    )
    return target


def get_user_or_404(db: Session, user_id: int) -> Usuario:
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return user

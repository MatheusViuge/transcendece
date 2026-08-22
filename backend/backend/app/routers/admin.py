from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.rbac import Permission, ROLE_PERMISSIONS, require_permissions
from app.core.response import success_response
from app.database import get_db
from app.models.specialty import Especialidade
from app.schemas.admin import AdminRoleUpdate, AdminStatusUpdate, AdminUserCreate, AdminUserResponse, AdminUserUpdate
from app.services.admin_user_service import (
    change_role,
    create_user,
    get_user_or_404,
    list_users,
    set_active_state,
    update_user,
)

router = APIRouter(prefix="/admin", tags=["Admin / RBAC"])
RoleFilter = Literal["aluno", "instrutor", "admin"]


def _serialize(user) -> AdminUserResponse:
    return AdminUserResponse.model_validate(user)


@router.get("/permissions")
def get_permission_matrix(usuario=Depends(require_permissions(Permission.ADMIN_USERS_READ))):
    del usuario
    return success_response(
        data={role: sorted(permission.value for permission in permissions) for role, permissions in ROLE_PERMISSIONS.items()},
        message="Matriz de permissões retornada com sucesso.",
    )


@router.get("/specialties")
def list_specialties(
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_READ)),
):
    del usuario
    items = db.query(Especialidade).order_by(Especialidade.nome.asc()).all()
    return success_response(
        data=[{"id": item.id, "nome": item.nome} for item in items],
        message="Especialidades listadas com sucesso.",
    )


@router.get("/users")
def admin_list_users(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(max_length=100)] = None,
    role: RoleFilter | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_READ)),
):
    del usuario
    items, total, total_pages = list_users(
        db,
        page=page,
        page_size=page_size,
        query=q,
        role=role,
        active=active,
    )
    return success_response(
        data={
            "items": [_serialize(item).model_dump(mode="json") for item in items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
        },
        message="Usuários administrativos listados com sucesso.",
    )


@router.post("/users", status_code=status.HTTP_201_CREATED)
def admin_create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_WRITE)),
):
    created = create_user(db, payload=payload, actor_id=usuario["id"])
    return success_response(
        data=_serialize(created),
        message="Usuário criado com sucesso.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/users/{user_id}")
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_READ)),
):
    del usuario
    target = get_user_or_404(db, user_id)
    return success_response(data=_serialize(target), message="Usuário encontrado com sucesso.")


@router.patch("/users/{user_id}")
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_WRITE)),
):
    target = get_user_or_404(db, user_id)
    updated = update_user(db, target=target, payload=payload, actor_id=usuario["id"])
    return success_response(data=_serialize(updated), message="Usuário atualizado com sucesso.")


@router.patch("/users/{user_id}/role")
def admin_change_role(
    user_id: int,
    payload: AdminRoleUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_ROLES_WRITE)),
):
    target = get_user_or_404(db, user_id)
    updated = change_role(
        db,
        target=target,
        new_role=payload.role,
        specialty_id=payload.especialidade_id,
        actor_id=usuario["id"],
    )
    return success_response(data=_serialize(updated), message="Role atualizada com sucesso.")


@router.patch("/users/{user_id}/status")
def admin_change_status(
    user_id: int,
    payload: AdminStatusUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_WRITE)),
):
    target = get_user_or_404(db, user_id)
    updated = set_active_state(
        db,
        target=target,
        is_active=payload.is_active,
        actor_id=usuario["id"],
    )
    return success_response(data=_serialize(updated), message="Status atualizado com sucesso.")


@router.delete("/users/{user_id}")
def admin_deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_permissions(Permission.ADMIN_USERS_WRITE)),
):
    target = get_user_or_404(db, user_id)
    updated = set_active_state(db, target=target, is_active=False, actor_id=usuario["id"])
    return success_response(
        data=_serialize(updated),
        message="Usuário desativado com sucesso; histórico foi preservado.",
    )

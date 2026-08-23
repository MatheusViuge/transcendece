from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import get_db
from app.models.user import Usuario
from app.schemas.user import (
    UsuarioAtualizarParcial,
    UsuarioPerfilPublicoResponse,
    UsuarioPerfilResponse,
)

router = APIRouter(prefix="/users", tags=["User Management"])


def _get_active_user(db: Session, user_id: int) -> Usuario:
    user = (
        db.query(Usuario)
        .filter(Usuario.id == user_id, Usuario.is_active.is_(True))
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return user


@router.get("/me", response_model=UsuarioPerfilResponse)
def get_own_profile(
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    """Retorna o perfil completo do usuário autenticado."""
    user = _get_active_user(db, identity["id"])
    return success_response(
        data=UsuarioPerfilResponse.model_validate(user),
        message="Perfil retornado com sucesso.",
    )


@router.patch("/me", response_model=UsuarioPerfilResponse)
def update_own_profile(
    payload: UsuarioAtualizarParcial,
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    """Atualiza somente campos de perfil permitidos do próprio usuário."""
    user = _get_active_user(db, identity["id"])
    changes = payload.model_dump(exclude_unset=True)

    if "email" in changes:
        email = str(changes["email"]).strip().lower()
        conflict = (
            db.query(Usuario)
            .filter(Usuario.email == email, Usuario.id != user.id)
            .first()
        )
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado.",
            )
        changes["email"] = email

    for field, value in changes.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return success_response(
        data=UsuarioPerfilResponse.model_validate(user),
        message="Perfil atualizado com sucesso.",
    )


@router.get("/{user_id}", response_model=UsuarioPerfilPublicoResponse)
def get_public_profile(
    user_id: int,
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles()),
):
    """Retorna apenas campos públicos do perfil de outro usuário."""
    del identity
    user = _get_active_user(db, user_id)
    return success_response(
        data=UsuarioPerfilPublicoResponse.model_validate(user),
        message="Perfil público retornado com sucesso.",
    )

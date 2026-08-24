from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles, create_access_token
from app.database import get_db
from app.models.user import Usuario
from app.schemas.user import TokenResponse, UsuarioCriar, UsuarioLogin, UsuarioResponse
from app.services.auth_service import get_password_hash, verify_password
from app.services.friend_code import generate_friend_code

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registra_usuario(usuario: UsuarioCriar, db: Session = Depends(get_db)):
    """Registra um usuário público sempre com a role segura padrão `aluno`."""
    email = str(usuario.email).strip().lower()
    ja_existe = db.query(Usuario).filter(Usuario.email == email).first()

    if ja_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já cadastrado.",
        )

    password_hash = get_password_hash(usuario.senha_hash)
    db_usuario: Usuario | None = None
    for _ in range(8):
        candidate = Usuario(
            nome=usuario.nome,
            sobrenome=usuario.sobrenome,
            email=email,
            senha_hash=password_hash,
            tipo_usuario="aluno",
            is_active=True,
            data_nascimento=usuario.data_nascimento,
            friend_code=generate_friend_code(),
        )
        db.add(candidate)
        try:
            db.commit()
            db.refresh(candidate)
            db_usuario = candidate
            break
        except IntegrityError:
            db.rollback()
            if db.query(Usuario).filter(Usuario.email == email).first() is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuário já cadastrado.",
                )

    if db_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível gerar um identificador público único. Tente novamente.",
        )

    return success_response(
        data=UsuarioResponse.model_validate(db_usuario),
        message="Usuário registrado com sucesso.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    require=Depends(allowed_roles("admin")),
):
    """Legacy endpoint; o CRUD completo vive em `/admin/users`."""
    del require
    usuarios = db.query(Usuario).all()

    return success_response(
        data=[UsuarioResponse.model_validate(usuario) for usuario in usuarios],
        message="Usuários listados com sucesso.",
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UsuarioLogin, db: Session = Depends(get_db)):
    """Autentica por email/senha e emite JWT somente após verificação do hash."""
    email = str(data.email).strip().lower()
    user = db.query(Usuario).filter(Usuario.email == email).first()

    if not user or not verify_password(data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )

    user.ultimo_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.tipo_usuario,
    )

    return success_response(
        data={"access_token": token, "token_type": "bearer"},
        message="Login realizado com sucesso.",
        status_code=status.HTTP_200_OK,
    )


@router.get("/me", response_model=UsuarioResponse)
def get_me(
    db: Session = Depends(get_db),
    usuario=Depends(allowed_roles()),
):
    """Retorna informações públicas do usuário autenticado."""
    user = db.query(Usuario).filter(Usuario.id == usuario["id"]).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário autenticado não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return success_response(
        data=UsuarioResponse.model_validate(user),
        message="Dados do usuário retornados com sucesso.",
        status_code=status.HTTP_200_OK,
    )

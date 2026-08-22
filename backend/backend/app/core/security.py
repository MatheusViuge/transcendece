from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from app.database import get_db
from app.models.user import Usuario

ALLOWED_ROLES = {"aluno", "instrutor", "admin"}


def create_access_token(user_id: int, email: str, role: str | None = None) -> str:
    """Cria um access token assinado.

    `role` é aceito por compatibilidade com callers antigos, mas autorização nunca
    confia na role do JWT: a role atual é consultada no banco em cada request.
    """
    del role
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email.strip().lower(),
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Verifica assinatura, expiração e claims mínimos do access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        email = payload.get("email")
        token_type = payload.get("type")

        if token_type != "access" or not isinstance(subject, str) or not subject.isdigit():
            raise credentials_exception
        if not isinstance(email, str) or not email.strip():
            raise credentials_exception

        return {
            "id": int(subject),
            "email": email.strip().lower(),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
        }
    except (JWTError, ValueError, TypeError):
        raise credentials_exception


def _token_user_from_request(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if user is not None:
        return user

    auth_header = request.headers.get("Authorization", "")
    scheme, separator, token = auth_header.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_token(token.strip())


def current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Resolve a identidade autenticada e a autorização corrente pelo banco.

    Isso evita sessão stale após mudança de role e invalida imediatamente contas
    desativadas, mesmo que o JWT ainda não tenha expirado.
    """
    token_user = _token_user_from_request(request)
    user = db.query(Usuario).filter(Usuario.id == token_user["id"]).first()

    if not user or user.email.strip().lower() != token_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )

    current_role = user.tipo_usuario
    if current_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role do usuário não é reconhecida.",
        )

    return {
        "id": user.id,
        "email": user.email,
        "role": current_role,
    }


def allowed_roles(*roles: str):
    """Autoriza usando a role atual persistida no banco.

    A assinatura `(request, db)` é mantida para compatibilidade com os testes e
    callers diretos existentes, enquanto o FastAPI injeta ambos normalmente.
    """
    unknown_roles = set(roles) - ALLOWED_ROLES
    if unknown_roles:
        raise ValueError(f"Roles desconhecidas configuradas na rota: {sorted(unknown_roles)}")

    def dependency(
        request: Request,
        db: Session = Depends(get_db),
    ) -> dict:
        usuario = current_user(request, db)
        if roles and usuario["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role não permitida.",
            )
        return usuario

    return dependency

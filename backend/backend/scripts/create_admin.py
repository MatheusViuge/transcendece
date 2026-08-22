from __future__ import annotations

import argparse
from datetime import date
from getpass import getpass

import app.models  # noqa: F401 - register SQLAlchemy models/relationships
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import Usuario
from app.schemas.admin import AdminUserCreate
from app.services.auth_service import get_password_hash


class BootstrapError(RuntimeError):
    pass


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _parse_birth_date(value: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise BootstrapError("Data de nascimento inválida. Use YYYY-MM-DD.") from exc


def _ensure_bootstrap_available(db: Session) -> None:
    if db.query(Usuario.id).filter(Usuario.tipo_usuario == "admin").first() is not None:
        raise BootstrapError(
            "Já existe uma conta admin. Use o painel /admin/usuarios para administrar outras contas."
        )


def create_first_admin(
    db: Session,
    *,
    nome: str,
    sobrenome: str,
    email: str,
    senha: str,
    data_nascimento: date,
) -> Usuario:
    # Keep this check even though main() performs the same preflight before
    # collecting credentials. It protects direct callers and re-checks the
    # database immediately before creation.
    _ensure_bootstrap_available(db)

    normalized_email = _normalize_email(email)
    if db.query(Usuario.id).filter(Usuario.email == normalized_email).first() is not None:
        raise BootstrapError(
            "O email informado já pertence a uma conta existente. O bootstrap não promove usuários existentes."
        )

    try:
        payload = AdminUserCreate(
            nome=nome,
            sobrenome=sobrenome,
            email=normalized_email,
            senha=senha,
            data_nascimento=data_nascimento,
            role="admin",
        )
    except ValidationError as exc:
        raise BootstrapError(str(exc)) from exc

    admin = Usuario(
        nome=payload.nome.strip(),
        sobrenome=payload.sobrenome.strip(),
        email=str(payload.email).strip().lower(),
        senha_hash=get_password_hash(payload.senha),
        data_nascimento=payload.data_nascimento,
        tipo_usuario="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def _prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print(f"{label} é obrigatório.")


def _prompt_password() -> str:
    while True:
        password = getpass("Password: ")
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            print("As senhas não coincidem.")
            continue
        return password


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria com segurança a primeira conta admin de uma instalação nova."
    )
    parser.add_argument("--email", help="Email do primeiro admin. Se omitido, será solicitado interativamente.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        # Fail fast before asking for any identity or password data when the
        # installation has already been bootstrapped.
        _ensure_bootstrap_available(db)

        nome = _prompt_required("Nome")
        sobrenome = _prompt_required("Sobrenome")
        email = args.email.strip() if args.email else _prompt_required("Email")
        data_nascimento = _parse_birth_date(_prompt_required("Data de nascimento (YYYY-MM-DD)"))
        senha = _prompt_password()

        admin = create_first_admin(
            db,
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            senha=senha,
            data_nascimento=data_nascimento,
        )
    except BootstrapError as exc:
        db.rollback()
        raise SystemExit(f"Bootstrap recusado: {exc}") from exc
    finally:
        db.close()

    print("Primeiro administrador criado com sucesso.")
    print(f"Admin: {admin.email}")


if __name__ == "__main__":
    main()

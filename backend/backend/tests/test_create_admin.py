from datetime import date

import pytest

from app.database import SessionLocal
from app.models.user import Usuario
from app.services.auth_service import verify_password
from scripts.create_admin import BootstrapError, create_first_admin


def _cleanup(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if user is not None:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_create_first_admin_creates_active_hashed_admin():
    email = "first.admin.bootstrap@example.com"
    _cleanup(email)

    db = SessionLocal()
    try:
        # Isolate the bootstrap scenario even if another test seeded an admin.
        existing_admins = db.query(Usuario).filter(Usuario.tipo_usuario == "admin").all()
        previous_roles = [(user.id, user.tipo_usuario) for user in existing_admins]
        for user in existing_admins:
            user.tipo_usuario = "aluno"
        db.commit()

        admin = create_first_admin(
            db,
            nome="First",
            sobrenome="Admin",
            email="  FIRST.ADMIN.BOOTSTRAP@EXAMPLE.COM ",
            senha="Secure42!",
            data_nascimento=date(1990, 1, 1),
        )

        assert admin.email == email
        assert admin.tipo_usuario == "admin"
        assert admin.is_active is True
        assert admin.senha_hash != "Secure42!"
        assert verify_password("Secure42!", admin.senha_hash)

        db.delete(admin)
        for user_id, role in previous_roles:
            user = db.query(Usuario).filter(Usuario.id == user_id).one()
            user.tipo_usuario = role
        db.commit()
    finally:
        db.close()


def test_bootstrap_refuses_when_any_admin_already_exists():
    db = SessionLocal()
    marker_email = "existing.bootstrap.admin@example.com"
    _cleanup(marker_email)
    try:
        existing = Usuario(
            nome="Existing",
            sobrenome="Admin",
            email=marker_email,
            senha_hash="not-used",
            data_nascimento=date(1990, 1, 1),
            tipo_usuario="admin",
            is_active=False,
        )
        db.add(existing)
        db.commit()

        with pytest.raises(BootstrapError, match="Já existe uma conta admin"):
            create_first_admin(
                db,
                nome="Another",
                sobrenome="Admin",
                email="another.bootstrap.admin@example.com",
                senha="Secure42!",
                data_nascimento=date(1990, 1, 1),
            )
    finally:
        existing = db.query(Usuario).filter(Usuario.email == marker_email).first()
        if existing is not None:
            db.delete(existing)
            db.commit()
        db.close()


def test_bootstrap_never_promotes_an_existing_non_admin_account():
    db = SessionLocal()
    email = "existing.student.bootstrap@example.com"
    _cleanup(email)
    try:
        admins = db.query(Usuario).filter(Usuario.tipo_usuario == "admin").all()
        previous_roles = [(user.id, user.tipo_usuario) for user in admins]
        for user in admins:
            user.tipo_usuario = "aluno"

        existing = Usuario(
            nome="Existing",
            sobrenome="Student",
            email=email,
            senha_hash="not-used",
            data_nascimento=date(1995, 1, 1),
            tipo_usuario="aluno",
            is_active=True,
        )
        db.add(existing)
        db.commit()

        with pytest.raises(BootstrapError, match="não promove usuários existentes"):
            create_first_admin(
                db,
                nome="Existing",
                sobrenome="Student",
                email=email,
                senha="Secure42!",
                data_nascimento=date(1995, 1, 1),
            )

        assert existing.tipo_usuario == "aluno"

        db.delete(existing)
        for user_id, role in previous_roles:
            user = db.query(Usuario).filter(Usuario.id == user_id).one()
            user.tipo_usuario = role
        db.commit()
    finally:
        db.close()

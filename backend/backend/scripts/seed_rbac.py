from __future__ import annotations

from datetime import date

import app.models  # noqa: F401

from app.database import SessionLocal
from app.models.user import Usuario
from app.services.auth_service import get_password_hash, verify_password
from scripts.seed_advanced_search import SEED_PASSWORD, populate as populate_search

RBAC_ADMIN_EMAIL = "admin.rbac@seed.example.com"
RBAC_ADMIN_PASSWORD = SEED_PASSWORD


def populate(db) -> Usuario:
    populate_search(db)
    admin = db.query(Usuario).filter(Usuario.email == RBAC_ADMIN_EMAIL).first()
    if admin is None:
        admin = Usuario(
            nome="Admin",
            sobrenome="RBAC",
            email=RBAC_ADMIN_EMAIL,
            data_nascimento=date(1990, 1, 1),
            tipo_usuario="admin",
            is_active=True,
            senha_hash=get_password_hash(RBAC_ADMIN_PASSWORD),
        )
        db.add(admin)
    else:
        admin.nome = "Admin"
        admin.sobrenome = "RBAC"
        admin.tipo_usuario = "admin"
        admin.is_active = True
        if not verify_password(RBAC_ADMIN_PASSWORD, admin.senha_hash):
            admin.senha_hash = get_password_hash(RBAC_ADMIN_PASSWORD)

    db.commit()
    db.refresh(admin)
    return admin


def main() -> None:
    db = SessionLocal()
    try:
        admin = populate(db)
        print("RBAC seed population ready.")
        print(f"Admin: {admin.email}")
        print(f"Password: {RBAC_ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

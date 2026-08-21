"""Configuração central de conexão com o PostgreSQL usando SQLAlchemy."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não foi definida. Configure a variável de ambiente antes de iniciar a API.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão SQLAlchemy por request e sempre fecha o recurso."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

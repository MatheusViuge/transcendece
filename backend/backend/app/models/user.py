from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Usuario(Base):
    """Modelo principal de autenticação e perfil do usuário."""

    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "tipo_usuario IN ('aluno', 'instrutor', 'admin')",
            name="ck_usuarios_tipo_usuario",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(45), nullable=False)
    sobrenome = Column(String(45), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(String(20), nullable=False, default="aluno")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())
    ultimo_login = Column(DateTime, nullable=True)
    ultima_atualizacao = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    avatar_file_id = Column(
        Integer,
        ForeignKey("uploaded_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    instrutor = relationship("Instrutor", back_populates="usuario", uselist=False)
    matriculas = relationship("Matricula", back_populates="aluno", cascade="all, delete-orphan")
    reviews_curso = relationship("AvaliacaoCurso", back_populates="usuario")
    api_keys = relationship("ApiKey", back_populates="owner", cascade="all, delete-orphan")
    uploaded_files = relationship(
        "UploadedFile",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="UploadedFile.owner_id",
    )
    avatar_file = relationship("UploadedFile", foreign_keys=[avatar_file_id], post_update=True)

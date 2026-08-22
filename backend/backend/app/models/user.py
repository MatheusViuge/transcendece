from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(45), nullable=False)
    sobrenome = Column(String(45), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo_usuario = Column(String(20), nullable=False, default="aluno", server_default="aluno")
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())
    ultimo_login = Column(DateTime, nullable=True)
    ultima_atualizacao = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    instrutor = relationship("Instrutor", back_populates="usuario", uselist=False)
    matriculas = relationship("Matricula", back_populates="aluno", cascade="all, delete-orphan")
    avaliacoes_curso = relationship("AvaliacaoCurso", back_populates="usuario", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="owner", cascade="all, delete-orphan")

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Matricula(Base):
    __tablename__ = "matriculas"
    __table_args__ = (
        UniqueConstraint("aluno_id", "curso_id", name="uq_matriculas_aluno_curso"),
    )

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=False)
    data_matricula = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    status_matricula = Column(String(12), nullable=False, default="ativa")
    data_conclusao = Column(DateTime(timezone=True), nullable=True)

    aluno = relationship("Usuario", back_populates="matriculas")
    curso = relationship("Curso", back_populates="matriculas")
    avaliacoes = relationship(
        "DesempenhoAluno",
        back_populates="matricula",
        cascade="all, delete-orphan",
    )
    progresso_aulas = relationship(
        "ProgressoAulas",
        back_populates="matricula",
        cascade="all, delete-orphan",
    )
    certificado = relationship(
        "Certificado",
        back_populates="matricula",
        uselist=False,
        cascade="all, delete-orphan",
    )

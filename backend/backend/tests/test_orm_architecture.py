from sqlalchemy import UniqueConstraint, inspect
from sqlalchemy.orm import configure_mappers

from app.database import Base, SessionLocal
from app.models.category import Categoria
from app.models.course import Curso
from app.models.enrollment import Matricula
from app.models.progress import ProgressoAulas
from app.models.user import Usuario
from app.repositories.category_repository import CategoryRepository


def test_active_models_have_resolvable_relational_metadata():
    """All active ORM mappings must configure and point FKs to registered tables."""
    configure_mappers()

    core_tables = {
        "usuarios",
        "categorias",
        "cursos",
        "matriculas",
        "progresso_aulas",
    }
    assert core_tables.issubset(Base.metadata.tables)
    assert "teste" not in Base.metadata.tables

    for table in Base.metadata.tables.values():
        assert len(table.primary_key.columns) > 0, f"{table.name} must have a primary key"
        for foreign_key in table.foreign_keys:
            assert foreign_key.column.table.name in Base.metadata.tables


def test_core_domain_relationships_are_explicit():
    assert {
        "instrutor",
        "matriculas",
        "reviews_curso",
    }.issubset(inspect(Usuario).relationships.keys())

    assert {
        "nivel",
        "instrutor",
        "categoria",
        "matriculas",
        "modulos",
        "avaliacoes_curso",
    }.issubset(inspect(Curso).relationships.keys())

    assert {
        "aluno",
        "curso",
        "avaliacoes",
        "progresso_aulas",
        "certificado",
    }.issubset(inspect(Matricula).relationships.keys())


def test_enrollment_and_progress_constraints_protect_identity():
    enrollment_unique_sets = {
        tuple(constraint.columns.keys())
        for constraint in Matricula.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("aluno_id", "curso_id") in enrollment_unique_sets

    progress_primary_key = tuple(ProgressoAulas.__table__.primary_key.columns.keys())
    assert progress_primary_key == ("matricula_id", "aula_id")


def test_category_repository_performs_real_orm_crud():
    db = SessionLocal()
    try:
        repository = CategoryRepository(db)

        category = repository.add(
            Categoria(nome="Arquitetura", descricao="Categoria usada pelo teste ORM."),
        )
        category_id = category.id

        assert category_id is not None
        assert repository.get_by_id(category_id) is category
        assert repository.get_by_name("Arquitetura") is category
        assert [item.id for item in repository.list_all()] == [category_id]

        category.descricao = "Descrição atualizada através do ORM."
        repository.save(category)
        assert repository.get_by_id(category_id).descricao == "Descrição atualizada através do ORM."

        repository.delete(category)
        assert repository.get_by_id(category_id) is None
    finally:
        db.close()

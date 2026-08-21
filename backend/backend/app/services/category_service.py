from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.category import Categoria
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoriaCreate, CategoriaUpdate


def list_categories(db: Session):
    return CategoryRepository(db).list_all()


def create_category(db: Session, payload: CategoriaCreate) -> Categoria:
    repository = CategoryRepository(db)

    if repository.get_by_name(payload.nome):
        raise AppException(
            "Categoria já existe.",
            status_code=status.HTTP_409_CONFLICT,
        )

    category = Categoria(nome=payload.nome, descricao=payload.descricao)

    try:
        return repository.add(category)
    except IntegrityError as exc:
        db.rollback()
        raise AppException(
            "Categoria já existe.",
            status_code=status.HTTP_409_CONFLICT,
        ) from exc


def update_category(db: Session, category_id: int, payload: CategoriaUpdate) -> Categoria:
    repository = CategoryRepository(db)
    category = repository.get_by_id(category_id)

    if category is None:
        raise AppException(
            f"Categoria com ID {category_id} não encontrada.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    update_data = payload.model_dump(exclude_unset=True)
    new_name = update_data.get("nome")

    if new_name:
        existing = repository.get_by_name(new_name)
        if existing is not None and existing.id != category_id:
            raise AppException(
                "Categoria já existe.",
                status_code=status.HTTP_409_CONFLICT,
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        return repository.save(category)
    except IntegrityError as exc:
        db.rollback()
        raise AppException(
            "Categoria já existe.",
            status_code=status.HTTP_409_CONFLICT,
        ) from exc


def delete_category(db: Session, category_id: int) -> None:
    repository = CategoryRepository(db)
    category = repository.get_by_id(category_id)

    if category is None:
        raise AppException(
            f"Categoria com ID {category_id} não encontrada.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    repository.delete(category)

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Categoria


class CategoryRepository:
    """SQLAlchemy ORM access for categories, isolated from HTTP concerns."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> Sequence[Categoria]:
        statement = select(Categoria).order_by(Categoria.id)
        return self.db.scalars(statement).all()

    def get_by_id(self, category_id: int) -> Categoria | None:
        return self.db.get(Categoria, category_id)

    def get_by_name(self, name: str) -> Categoria | None:
        statement = select(Categoria).where(Categoria.nome == name)
        return self.db.scalar(statement)

    def add(self, category: Categoria) -> Categoria:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def save(self, category: Categoria) -> Categoria:
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Categoria) -> None:
        self.db.delete(category)
        self.db.commit()

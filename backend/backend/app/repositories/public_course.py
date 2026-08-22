from __future__ import annotations

from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.category import Categoria
from app.models.course import Curso
from app.models.instructor import Instrutor
from app.models.level import Nivel
from app.schemas.public_api import (
    PublicCourse,
    PublicCourseCreate,
    PublicCoursePage,
    PublicCourseUpdate,
    PublicPagination,
    PublicReference,
)


def _course_query(db: Session):
    return db.query(Curso).options(
        joinedload(Curso.categoria),
        joinedload(Curso.nivel),
        joinedload(Curso.instrutor).joinedload(Instrutor.usuario),
    )


def _serialize(course: Curso) -> PublicCourse:
    instructor_user = course.instrutor.usuario
    return PublicCourse(
        id=course.id,
        title=course.titulo,
        description=course.descricao,
        price=float(course.preco),
        workload_hours=course.carga_horaria,
        image_url=course.url_image,
        category=PublicReference(id=course.categoria.id, name=course.categoria.nome),
        level=PublicReference(id=course.nivel.id, name=course.nivel.descricao),
        instructor=PublicReference(
            id=course.instrutor_id,
            name=f"{instructor_user.nome} {instructor_user.sobrenome}".strip(),
        ),
        created_at=course.data_criacao,
        updated_at=course.ultima_atualizacao,
    )


def _validate_references(db: Session, *, category_id: int, level_id: int) -> None:
    if db.query(Categoria.id).filter(Categoria.id == category_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="category_id não existe.")
    if db.query(Nivel.id).filter(Nivel.id == level_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="level_id não existe.")


def list_courses(db: Session, *, page: int, page_size: int) -> PublicCoursePage:
    query = _course_query(db).order_by(Curso.id.asc())
    total = query.order_by(None).count()
    courses = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = ceil(total / page_size) if total else 0
    return PublicCoursePage(
        items=[_serialize(course) for course in courses],
        pagination=PublicPagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_previous=page > 1,
            has_next=page < total_pages,
        ),
    )


def get_course(db: Session, *, course_id: int) -> PublicCourse:
    course = _course_query(db).filter(Curso.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado.")
    return _serialize(course)


def create_course(db: Session, *, owner_id: int, payload: PublicCourseCreate) -> PublicCourse:
    _validate_references(db, category_id=payload.category_id, level_id=payload.level_id)
    course = Curso(
        titulo=payload.title,
        descricao=payload.description,
        preco=payload.price,
        carga_horaria=payload.workload_hours,
        categoria_id=payload.category_id,
        nivel_id=payload.level_id,
        instrutor_id=owner_id,
        url_image=payload.image_url,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return get_course(db, course_id=course.id)


def _owned_course(db: Session, *, course_id: int, owner_id: int) -> Curso:
    course = (
        db.query(Curso)
        .filter(Curso.id == course_id, Curso.instrutor_id == owner_id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado.")
    return course


def update_course(
    db: Session,
    *,
    course_id: int,
    owner_id: int,
    payload: PublicCourseUpdate,
) -> PublicCourse:
    course = _owned_course(db, course_id=course_id, owner_id=owner_id)
    changes = payload.model_dump(exclude_unset=True)

    category_id = changes.get("category_id", course.categoria_id)
    level_id = changes.get("level_id", course.nivel_id)
    _validate_references(db, category_id=category_id, level_id=level_id)

    mapping = {
        "title": "titulo",
        "description": "descricao",
        "price": "preco",
        "workload_hours": "carga_horaria",
        "category_id": "categoria_id",
        "level_id": "nivel_id",
        "image_url": "url_image",
    }
    for public_name, model_name in mapping.items():
        if public_name in changes:
            setattr(course, model_name, changes[public_name])

    db.commit()
    return get_course(db, course_id=course.id)


def delete_course(db: Session, *, course_id: int, owner_id: int) -> None:
    course = _owned_course(db, course_id=course_id, owner_id=owner_id)
    db.delete(course)
    db.commit()

from __future__ import annotations

from math import ceil

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.category import Categoria
from app.models.course import Curso
from app.models.evaluation import AvaliacaoCurso
from app.models.instructor import Instrutor
from app.models.level import Nivel
from app.models.user import Usuario
from app.schemas.search import (
    CourseSearchData,
    CourseSearchFacets,
    CourseSearchItem,
    PaginationMetadata,
    SearchOption,
)


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _facets(db: Session) -> CourseSearchFacets:
    categories = [
        SearchOption(id=item.id, label=item.nome)
        for item in db.query(Categoria).order_by(func.lower(Categoria.nome), Categoria.id).all()
    ]
    levels = [
        SearchOption(id=item.id, label=item.descricao)
        for item in db.query(Nivel).order_by(func.lower(Nivel.descricao), Nivel.id).all()
    ]
    instructors = [
        SearchOption(id=instructor.id, label=f"{user.nome} {user.sobrenome}".strip())
        for instructor, user in (
            db.query(Instrutor, Usuario)
            .join(Usuario, Usuario.id == Instrutor.id)
            .order_by(func.lower(Usuario.nome), func.lower(Usuario.sobrenome), Instrutor.id)
            .all()
        )
    ]
    return CourseSearchFacets(
        categories=categories,
        levels=levels,
        instructors=instructors,
    )


def search_courses(
    db: Session,
    *,
    query_text: str | None,
    category_id: int | None,
    level_id: int | None,
    instructor_id: int | None,
    price: str | None,
    sort: str,
    order: str,
    page: int,
    page_size: int,
) -> CourseSearchData:
    rating_summary = (
        db.query(
            AvaliacaoCurso.curso_id.label("curso_id"),
            func.avg(AvaliacaoCurso.nota).label("avaliacao"),
            func.count(AvaliacaoCurso.id).label("quantidade_avaliacoes"),
        )
        .group_by(AvaliacaoCurso.curso_id)
        .subquery()
    )

    rating_expr = func.coalesce(rating_summary.c.avaliacao, 0.0)
    rating_count_expr = func.coalesce(rating_summary.c.quantidade_avaliacoes, 0)

    base_query = (
        db.query(
            Curso.id,
            Curso.url_image,
            Curso.titulo,
            Curso.descricao,
            Curso.instrutor_id,
            Usuario.nome.label("instrutor_nome"),
            Usuario.sobrenome.label("instrutor_sobrenome"),
            Curso.nivel_id,
            Nivel.descricao.label("nivel"),
            Curso.categoria_id,
            Categoria.nome.label("categoria"),
            Curso.preco,
            Curso.data_criacao,
            rating_expr.label("avaliacao"),
            rating_count_expr.label("quantidade_avaliacoes"),
        )
        .join(Categoria, Categoria.id == Curso.categoria_id)
        .join(Nivel, Nivel.id == Curso.nivel_id)
        .join(Instrutor, Instrutor.id == Curso.instrutor_id)
        .join(Usuario, Usuario.id == Instrutor.id)
        .outerjoin(rating_summary, rating_summary.c.curso_id == Curso.id)
    )

    normalized_query = (query_text or "").strip()
    if normalized_query:
        pattern = f"%{_escape_like(normalized_query)}%"
        base_query = base_query.filter(
            or_(
                Curso.titulo.ilike(pattern, escape="\\"),
                Curso.descricao.ilike(pattern, escape="\\"),
                Categoria.nome.ilike(pattern, escape="\\"),
                Nivel.descricao.ilike(pattern, escape="\\"),
                Usuario.nome.ilike(pattern, escape="\\"),
                Usuario.sobrenome.ilike(pattern, escape="\\"),
            )
        )

    if category_id is not None:
        base_query = base_query.filter(Curso.categoria_id == category_id)
    if level_id is not None:
        base_query = base_query.filter(Curso.nivel_id == level_id)
    if instructor_id is not None:
        base_query = base_query.filter(Curso.instrutor_id == instructor_id)
    if price == "free":
        base_query = base_query.filter(Curso.preco <= 0)
    elif price == "paid":
        base_query = base_query.filter(Curso.preco > 0)

    total = base_query.order_by(None).count()

    sort_expressions = {
        "title": func.lower(Curso.titulo),
        "price": Curso.preco,
        "rating": rating_expr,
        "newest": Curso.data_criacao,
    }
    sort_expression = sort_expressions[sort]
    ordered = sort_expression.desc() if order == "desc" else sort_expression.asc()

    rows = (
        base_query.order_by(ordered, Curso.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        CourseSearchItem(
            id=row.id,
            url_image=row.url_image,
            titulo=row.titulo,
            descricao=row.descricao,
            id_instrutor=row.instrutor_id,
            instrutor=f"{row.instrutor_nome} {row.instrutor_sobrenome}".strip(),
            id_nivel=row.nivel_id,
            nivel=row.nivel,
            id_categoria=row.categoria_id,
            categoria=row.categoria,
            avaliacao=float(row.avaliacao or 0.0),
            quantidade_avaliacoes=int(row.quantidade_avaliacoes or 0),
            preco=float(row.preco or 0.0),
        )
        for row in rows
    ]

    total_pages = ceil(total / page_size) if total else 0
    return CourseSearchData(
        items=items,
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_previous=page > 1,
            has_next=page < total_pages,
        ),
        facets=_facets(db),
    )

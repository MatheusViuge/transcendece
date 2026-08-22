from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.database import get_db
from app.repositories.course_search import search_courses

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/courses")
def advanced_course_search(
    q: str | None = Query(default=None, max_length=120),
    category_id: int | None = Query(default=None, gt=0),
    level_id: int | None = Query(default=None, gt=0),
    instructor_id: int | None = Query(default=None, gt=0),
    price: Literal["free", "paid"] | None = Query(default=None),
    sort: Literal["title", "price", "rating", "newest"] = Query(default="newest"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=48),
    db: Session = Depends(get_db),
):
    """Busca pública de cursos persistidos com filtros, sorting e paginação server-side."""
    data = search_courses(
        db,
        query_text=q,
        category_id=category_id,
        level_id=level_id,
        instructor_id=instructor_id,
        price=price,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    return success_response(
        data=data,
        message="Busca de cursos realizada com sucesso.",
        status_code=status.HTTP_200_OK,
    )

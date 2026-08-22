from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.api_key_auth import ApiKeyContext, require_api_key
from app.core.response import success_response
from app.database import get_db
from app.repositories.public_course import (
    create_course,
    delete_course,
    get_course,
    list_courses,
    update_course,
)
from app.schemas.public_api import PublicCourseCreate, PublicCourseUpdate

router = APIRouter(prefix="/v1/public", tags=["Public API v1"])


def _with_rate_headers(response, context: ApiKeyContext):
    for key, value in context.rate_headers.items():
        response.headers[key] = value
    return response


def _require_instructor(context: ApiKeyContext) -> None:
    if context.owner_role != "instrutor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A escrita de cursos exige uma API key pertencente a um instrutor.",
        )


@router.get("/courses")
def public_list_courses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    context: ApiKeyContext = Depends(require_api_key("courses:read")),
):
    response = success_response(
        data=list_courses(db, page=page, page_size=page_size),
        message="Cursos públicos retornados com sucesso.",
    )
    return _with_rate_headers(response, context)


@router.get("/courses/{course_id}")
def public_get_course(
    course_id: int,
    db: Session = Depends(get_db),
    context: ApiKeyContext = Depends(require_api_key("courses:read")),
):
    response = success_response(
        data=get_course(db, course_id=course_id),
        message="Curso público retornado com sucesso.",
    )
    return _with_rate_headers(response, context)


@router.post("/courses", status_code=status.HTTP_201_CREATED)
def public_create_course(
    payload: PublicCourseCreate,
    db: Session = Depends(get_db),
    context: ApiKeyContext = Depends(require_api_key("courses:write")),
):
    _require_instructor(context)
    response = success_response(
        data=create_course(db, owner_id=context.owner_id, payload=payload),
        message="Curso criado através da Public API.",
        status_code=status.HTTP_201_CREATED,
    )
    return _with_rate_headers(response, context)


@router.put("/courses/{course_id}")
def public_update_course(
    course_id: int,
    payload: PublicCourseUpdate,
    db: Session = Depends(get_db),
    context: ApiKeyContext = Depends(require_api_key("courses:write")),
):
    _require_instructor(context)
    response = success_response(
        data=update_course(
            db,
            course_id=course_id,
            owner_id=context.owner_id,
            payload=payload,
        ),
        message="Curso atualizado através da Public API.",
    )
    return _with_rate_headers(response, context)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def public_delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    context: ApiKeyContext = Depends(require_api_key("courses:write")),
):
    _require_instructor(context)
    delete_course(db, course_id=course_id, owner_id=context.owner_id)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    return _with_rate_headers(response, context)

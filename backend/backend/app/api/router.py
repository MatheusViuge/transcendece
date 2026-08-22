from fastapi import APIRouter

from app.routers import (
    auth,
    category,
    course,
    enrollments,
    evaluation,
    instructor,
    level,
    search,
)

api_router = APIRouter()

for router in (
    auth.router,
    category.router,
    level.router,
    search.router,
    course.router,
    instructor.router,
    evaluation.router,
    enrollments.router,
):
    api_router.include_router(router)

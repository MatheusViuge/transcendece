from fastapi import APIRouter

from app.routers import (
    api_keys,
    auth,
    category,
    course,
    enrollments,
    evaluation,
    instructor,
    level,
    public_api,
    search,
)

api_router = APIRouter()

for router in (
    auth.router,
    api_keys.router,
    category.router,
    level.router,
    search.router,
    public_api.router,
    course.router,
    instructor.router,
    evaluation.router,
    enrollments.router,
):
    api_router.include_router(router)

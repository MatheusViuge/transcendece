from fastapi import APIRouter

from app.routers import (
    admin,
    api_keys,
    auth,
    category,
    course,
    enrollments,
    evaluation,
    files,
    instructor,
    level,
    public_api,
    search,
    users,
)

api_router = APIRouter()

for router in (
    auth.router,
    admin.router,
    api_keys.router,
    category.router,
    level.router,
    search.router,
    public_api.router,
    files.router,
    users.router,
    course.router,
    instructor.router,
    evaluation.router,
    enrollments.router,
):
    api_router.include_router(router)

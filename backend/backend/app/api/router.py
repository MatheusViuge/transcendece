from fastapi import APIRouter

from app.routers import (
    admin,
    analytics,
    api_keys,
    auth,
    category,
    chat,
    course,
    enrollments,
    evaluation,
    files,
    instructor,
    level,
    public_api,
    realtime,
    search,
    users,
)

api_router = APIRouter()

for router in (
    auth.router,
    admin.router,
    analytics.router,
    analytics.ws_router,
    api_keys.router,
    category.router,
    level.router,
    search.router,
    public_api.router,
    files.router,
    users.router,
    chat.router,
    realtime.router,
    course.router,
    instructor.router,
    evaluation.router,
    enrollments.router,
):
    api_router.include_router(router)

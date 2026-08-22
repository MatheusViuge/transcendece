from fastapi import FastAPI

from app.api.router import api_router
from app.core.cors import register_cors_middleware
from app.core.error_handlers import register_exception_handlers
from app.core.middleware import register_jwt_middleware


def create_app() -> FastAPI:
    """Application factory used by Uvicorn and the automated test suite."""
    application = FastAPI(
        title="Instituto Consuelo API",
        description="Backend da plataforma educacional Instituto Consuelo.",
        version="1.0.0",
        root_path="/api",
    )

    register_jwt_middleware(application)
    register_cors_middleware(application)
    application.include_router(api_router)
    register_exception_handlers(application)

    @application.get("/", include_in_schema=False)
    def root():
        return {"status": "ok"}

    @application.get("/status", tags=["health"])
    def status():
        return {"status": "ok"}

    return application


app = create_app()

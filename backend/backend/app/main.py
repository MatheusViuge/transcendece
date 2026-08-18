from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from app.core import middleware
from app.core.error_handlers import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from app.database import Base, engine
from app.routers import (
    auth,
    category,
    course,
    enrollments,
    evaluation,
    instructor,
    level,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Instituto Consuelo API",
    description="Backend da plataforma educacional Instituto Consuelo.",
    version="1.0.0",
    root_path="/api",
)

middleware.register_jwt_middleware(app)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://localhost",
    "https://127.0.0.1",
    "https://plataforma-instituto-consuelo.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(level.router)
app.include_router(course.router)
app.include_router(instructor.router)
app.include_router(evaluation.router)
app.include_router(enrollments.router)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok"}


@app.get("/status", tags=["health"])
def status():
    return {"status": "ok"}

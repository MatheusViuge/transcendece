from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.schemas.error import ErrorResponse


async def app_exception_handler(request: Request, exc: AppException):
    del request
    payload = ErrorResponse(
        data=exc.data,
        message=exc.message,
    )
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(payload))


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    del request
    # Pydantic custom validators may keep the original exception object inside
    # `ctx`. Sanitize the raw error list before putting it inside ErrorResponse,
    # otherwise Pydantic's own model serializer sees ValueError first and fails
    # while trying to return the intended 422 response.
    errors = jsonable_encoder(
        exc.errors(),
        custom_encoder={BaseException: str},
    )
    payload = ErrorResponse(
        data=errors,
        message="Erro de validação na requisição.",
    )
    return JSONResponse(status_code=422, content=jsonable_encoder(payload))


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    del request
    payload = ErrorResponse(
        data=None,
        message=str(exc.detail) if exc.detail else "Erro na requisição.",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(payload),
        headers=exc.headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    del request, exc
    payload = ErrorResponse(
        data=None,
        message="Erro interno inesperado.",
    )
    return JSONResponse(status_code=500, content=jsonable_encoder(payload))


def register_exception_handlers(app: FastAPI) -> None:
    """Keep the public error envelope consistent across the application."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.security import verify_token

PUBLIC_PATHS = {
    "/",
    "/status",
    "/auth/login",
    "/auth/register",
    "/courses",
    "/docs",
    "/redoc",
    "/openapi.json",
}


def _is_public_request(request: Request, normalized_path: str) -> bool:
    if request.method == "OPTIONS":
        return True

    if normalized_path in PUBLIC_PATHS:
        return True

    if request.method != "GET":
        return False

    if normalized_path.startswith("/courses/"):
        parts = normalized_path.split("/")

        if len(parts) == 3 and parts[2].isdigit():
            return True

        if len(parts) == 4 and parts[2].isdigit() and parts[3] in {"modules", "reviews"}:
            return True

    return False


def register_jwt_middleware(app):
    """Valida access tokens das rotas protegidas e popula `request.state.user`."""

    @app.middleware("http")
    async def jwt_middleware(request: Request, call_next):
        try:
            normalized_path = request.url.path.rstrip("/") or "/"

            if _is_public_request(request, normalized_path):
                return await call_next(request)

            auth_header = request.headers.get("Authorization", "")
            scheme, separator, token = auth_header.partition(" ")

            if separator != " " or scheme.lower() != "bearer" or not token.strip():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token não fornecido.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            request.state.user = verify_token(token.strip())
            return await call_next(request)

        except HTTPException as exc:
            headers = exc.headers or {}
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=headers,
            )

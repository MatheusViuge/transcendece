from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = (
    "http://localhost:5173",
    "http://localhost:3000",
    "https://localhost",
    "https://127.0.0.1",
    "https://plataforma-instituto-consuelo.vercel.app",
)


def register_cors_middleware(app: FastAPI) -> None:
    """Register the CORS policy used by local and deployed frontend clients."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

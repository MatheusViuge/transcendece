from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import get_db
from app.schemas.category import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.schemas.success import SuccessResponse
from app.services.category_service import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])
DbSession = Annotated[Session, Depends(get_db)]
AdminAccess = Annotated[dict, Depends(allowed_roles("admin"))]


@router.post("/", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def cria_categoria(
    categoria_request: CategoriaCreate,
    db: DbSession,
    require: AdminAccess,
):
    del require
    category = create_category(db, categoria_request)
    return success_response(
        data=CategoriaResponse.model_validate(category),
        message="Categoria criada com sucesso.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/", response_model=SuccessResponse)
def listar_categoria(db: DbSession):
    categories = list_categories(db)
    return success_response(
        data=[CategoriaResponse.model_validate(category) for category in categories],
        message="Categorias listadas com sucesso.",
    )


@router.patch("/{id_categoria}", response_model=SuccessResponse)
def atualiza_categoria(
    id_categoria: int,
    categoria_update: CategoriaUpdate,
    db: DbSession,
    require: AdminAccess,
):
    del require
    category = update_category(db, id_categoria, categoria_update)
    return success_response(
        data=CategoriaResponse.model_validate(category),
        message="Categoria atualizada com sucesso.",
    )


@router.delete("/{id_categoria}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def deleta_categoria(
    id_categoria: int,
    db: DbSession,
    require: AdminAccess,
):
    del require
    delete_category(db, id_categoria)
    return success_response(
        data=None,
        message="Categoria removida com sucesso.",
        status_code=status.HTTP_200_OK,
    )

from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import StrictInputModel

NameType = Annotated[str, Field(min_length=1, max_length=100, description="Nome da categoria")]
DescriptionType = Annotated[str, Field(min_length=1, max_length=500, description="Descrição da categoria")]


class CategoriaCreate(StrictInputModel):
    nome: NameType
    descricao: DescriptionType


class CategoriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: NameType
    descricao: DescriptionType


class CategoriaUpdate(StrictInputModel):
    nome: Optional[NameType] = None
    descricao: Optional[DescriptionType] = None

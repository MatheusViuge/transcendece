from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import StrictInputModel

DescriptionType = Annotated[str, Field(min_length=1, max_length=20, description="Descrição do nível")]


class NivelCreate(StrictInputModel):
    descricao: DescriptionType


class NivelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descricao: DescriptionType


class NivelUpdate(StrictInputModel):
    descricao: Optional[DescriptionType] = None

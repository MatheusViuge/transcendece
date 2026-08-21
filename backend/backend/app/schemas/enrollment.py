from typing import Annotated, Literal, Optional

from pydantic import Field

from app.schemas.base import StrictInputModel

PositiveId = Annotated[int, Field(gt=0)]
EnrollmentStatus = Literal["ativa", "cancelada", "concluida"]


class EnrollmentCreate(StrictInputModel):
    id_curso: PositiveId
    id_aluno: Optional[PositiveId] = None

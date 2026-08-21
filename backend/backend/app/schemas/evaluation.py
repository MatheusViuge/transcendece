from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import StrictInputModel

NotaType = Annotated[int, Field(ge=1, le=5, description="Nota da avaliação (1-5)")]
ComentarioType = Annotated[Optional[str], Field(max_length=500, description="Comentário opcional")]


class AvaliacaoCriar(StrictInputModel):
    """Payload aceito para criação; curso e usuário vêm da URL/autenticação."""

    nota: NotaType
    comentario: ComentarioType = None


class AvaliacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    curso_id: int
    usuario_id: int
    nota: NotaType
    comentario: ComentarioType = None
    data_criacao: datetime

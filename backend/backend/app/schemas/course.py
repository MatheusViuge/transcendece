from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import StrictInputModel

TituloType = Annotated[str, Field(max_length=200, min_length=1, description="Título do curso")]
DescricaoType = Annotated[str, Field(max_length=500, min_length=1, description="Descrição do curso")]
CargaHorariaType = Annotated[int, Field(gt=0, description="Carga horária do curso")]
IdInstrutorType = Annotated[int, Field(gt=0, description="ID do instrutor")]
IdNivelType = Annotated[int, Field(gt=0, description="ID do nível")]
IdCategoriaType = Annotated[int, Field(gt=0, description="ID da categoria")]
InstrutorOrNivel = Annotated[str, Field(max_length=200, description="Nome do instrutor ou nível")]
MediaAvaliacao = Annotated[float, Field(ge=0, le=5, description="Média de avaliações")]
QtdAvaliacao = Annotated[int, Field(ge=0, description="Quantidade de avaliações")]
PrecoType = Annotated[float, Field(ge=0, description="Preço do curso")]
UrlImageType = Annotated[str, Field(max_length=255, description="URL da imagem do curso")]
PrecoOptionalType = Annotated[Optional[float], Field(ge=0, description="Preço do curso")]


class CursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url_image: Optional[UrlImageType] = None
    titulo: TituloType
    id_instrutor: int
    instrutor: InstrutorOrNivel
    id_nivel: int
    nivel: InstrutorOrNivel
    avaliacao: MediaAvaliacao = 0.0
    quantidade_avaliacoes: QtdAvaliacao = 0
    preco: PrecoType = 0.0


class CursoEspecificoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: TituloType
    descricao: DescricaoType
    avaliacao: MediaAvaliacao = 0.0
    quantidade_avaliacoes: QtdAvaliacao = 0
    quantidade_horas: CargaHorariaType
    id_nivel: int
    nivel: InstrutorOrNivel
    preco: PrecoType = 0.0
    id_instrutor: int
    instrutor: InstrutorOrNivel
    id_especialidade: int
    especialidade_instrutor: str


class CursoControleBase(StrictInputModel):
    titulo: TituloType
    descricao: DescricaoType
    id_categoria: IdCategoriaType
    id_nivel: IdNivelType
    id_instrutor: Optional[IdInstrutorType] = None
    preco: PrecoOptionalType = 0.0


class CursoControleCriar(CursoControleBase):
    pass


class CursoControleAtualizar(CursoControleBase):
    id: Annotated[int, Field(gt=0)]


class CursoControleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: TituloType
    descricao: DescricaoType
    id_categoria: IdCategoriaType
    id_nivel: IdNivelType
    id_instrutor: Optional[IdInstrutorType] = None
    preco: PrecoOptionalType = 0.0
    sobre: float = 0.0


class CursoEstatisticaItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    id_categoria: int
    categoria: str
    id_nivel: int
    nivel: str
    id_instrutor: int
    instrutor: str
    percentual_conclusao: Annotated[float, Field(ge=0, le=100)]
    media_notas: Annotated[float, Field(ge=0, le=5)]
    quantidade_alunos: Annotated[int, Field(ge=0)]
    data_criacao: datetime
    data_publicacao: Optional[datetime]

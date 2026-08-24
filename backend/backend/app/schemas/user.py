from datetime import date, datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.base import StrictInputModel

TipoUser = Literal["instrutor", "aluno", "admin"]

NomeType = Annotated[str, Field(min_length=1, max_length=45, description="Nome")]
SobrenomeType = Annotated[str, Field(min_length=1, max_length=45, description="Sobrenome")]
SenhaType = Annotated[str, Field(min_length=6, max_length=128, description="Senha em texto")]
EmailType = Annotated[EmailStr, Field(description="Email válido")]


def _validate_birth_date(value: Optional[date]) -> Optional[date]:
    if value is not None and value >= date.today():
        raise ValueError("A data de nascimento deve estar no passado.")
    return value


class UsuarioCriar(StrictInputModel):
    nome: NomeType
    sobrenome: SobrenomeType
    email: EmailType
    senha_hash: SenhaType
    data_nascimento: date

    @field_validator("senha_hash")
    @classmethod
    def validar_forca_senha(cls, value: str) -> str:
        if not any(char.isalpha() for char in value):
            raise ValueError("A senha deve conter pelo menos uma letra.")
        if not any(char.isdigit() for char in value):
            raise ValueError("A senha deve conter pelo menos um número.")
        if not any(not char.isalnum() for char in value):
            raise ValueError("A senha deve conter pelo menos um caractere especial.")
        return value

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, value: date) -> date:
        return _validate_birth_date(value)  # type: ignore[return-value]


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: NomeType
    sobrenome: SobrenomeType
    email: EmailType
    tipo_usuario: TipoUser
    data_cadastro: datetime
    ultimo_login: Optional[datetime]


class UsuarioPerfilResponse(UsuarioResponse):
    data_nascimento: date
    ultima_atualizacao: datetime


class UsuarioPerfilPublicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: NomeType
    sobrenome: SobrenomeType
    tipo_usuario: TipoUser
    data_cadastro: datetime


class UsuarioAtualizarTudo(StrictInputModel):
    nome: NomeType
    sobrenome: SobrenomeType
    email: EmailType
    data_nascimento: date

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, value: date) -> date:
        return _validate_birth_date(value)  # type: ignore[return-value]


class UsuarioAtualizarParcial(StrictInputModel):
    nome: Optional[NomeType] = None
    sobrenome: Optional[SobrenomeType] = None
    email: Optional[EmailType] = None
    data_nascimento: Optional[date] = None

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, value: Optional[date]) -> Optional[date]:
        return _validate_birth_date(value)


class UsuarioLogin(StrictInputModel):
    email: EmailStr
    senha: Annotated[str, Field(min_length=1, max_length=128)]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioAdminUpdate(StrictInputModel):
    tipo_usuario: TipoUser

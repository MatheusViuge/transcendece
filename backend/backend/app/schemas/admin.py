from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.base import StrictInputModel

UserRole = Literal["aluno", "instrutor", "admin"]


class AdminUserCreate(StrictInputModel):
    nome: Annotated[str, Field(min_length=1, max_length=45)]
    sobrenome: Annotated[str, Field(min_length=1, max_length=45)]
    email: EmailStr
    senha: Annotated[str, Field(min_length=6, max_length=128)]
    data_nascimento: date
    role: UserRole = "aluno"
    especialidade_id: Annotated[int | None, Field(gt=0)] = None

    @field_validator("senha")
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
        if value >= date.today():
            raise ValueError("A data de nascimento deve estar no passado.")
        return value

    @model_validator(mode="after")
    def validar_instrutor(self):
        if self.role == "instrutor" and self.especialidade_id is None:
            raise ValueError("especialidade_id é obrigatório para instrutores.")
        return self


class AdminUserUpdate(StrictInputModel):
    nome: Annotated[str | None, Field(min_length=1, max_length=45)] = None
    sobrenome: Annotated[str | None, Field(min_length=1, max_length=45)] = None
    email: EmailStr | None = None
    data_nascimento: date | None = None

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, value: date | None) -> date | None:
        if value is not None and value >= date.today():
            raise ValueError("A data de nascimento deve estar no passado.")
        return value


class AdminRoleUpdate(StrictInputModel):
    role: UserRole
    especialidade_id: Annotated[int | None, Field(gt=0)] = None


class AdminStatusUpdate(StrictInputModel):
    is_active: bool


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    sobrenome: str
    email: EmailStr
    data_nascimento: date
    tipo_usuario: UserRole
    is_active: bool
    data_cadastro: datetime
    ultimo_login: datetime | None


class AdminUserPage(BaseModel):
    items: list[AdminUserResponse]
    page: int
    page_size: int
    total: int
    total_pages: int

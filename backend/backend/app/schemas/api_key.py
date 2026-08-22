from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ApiKeyScope = Literal["courses:read", "courses:write"]


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    scopes: list[ApiKeyScope] | None = None


class ApiKeyInfo(BaseModel):
    id: int
    name: str
    prefix: str
    scopes: list[str]
    created_at: datetime
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None
    active: bool


class ApiKeyCreated(ApiKeyInfo):
    secret: str = Field(
        description="Secret exibido uma única vez. Armazene-o com segurança.",
    )

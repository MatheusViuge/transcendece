from pydantic import BaseModel, ConfigDict


class StrictInputModel(BaseModel):
    """Base para payloads recebidos pela API.

    Campos desconhecidos são rejeitados e strings são normalizadas com trim.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

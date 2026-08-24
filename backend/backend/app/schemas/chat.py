from pydantic import BaseModel, Field, field_validator


class ConversationCreate(BaseModel):
    recipient_id: int = Field(gt=0)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("A mensagem não pode ser vazia.")
        if len(normalized) > 2000:
            raise ValueError("A mensagem deve ter no máximo 2000 caracteres.")
        return normalized

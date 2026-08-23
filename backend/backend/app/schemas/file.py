from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadedFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    content_type: str
    size_bytes: int
    sha256: str
    purpose: str
    created_at: datetime
    content_url: str

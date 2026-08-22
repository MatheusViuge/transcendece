from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ApiKey(Base):
    """API key persistida sem armazenar o secret utilizável em texto puro."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    prefix = Column(String(24), nullable=False, unique=True, index=True)
    key_hash = Column(String(64), nullable=False, unique=True)
    scopes = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    rate_window_started_at = Column(DateTime(timezone=True), nullable=True)
    rate_request_count = Column(Integer, nullable=False, default=0, server_default="0")

    owner = relationship("Usuario", back_populates="api_keys")

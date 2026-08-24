from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class Friendship(Base):
    __tablename__ = "friendships"
    __table_args__ = (
        CheckConstraint("user_low_id < user_high_id", name="ck_friendships_order"),
        UniqueConstraint("user_low_id", "user_high_id", name="uq_friendships_pair"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_low_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    user_high_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class FriendRequest(Base):
    __tablename__ = "friend_requests"
    __table_args__ = (
        CheckConstraint("user_low_id < user_high_id", name="ck_friend_requests_order"),
        CheckConstraint(
            "requester_id = user_low_id OR requester_id = user_high_id",
            name="ck_friend_requests_requester_participant",
        ),
        UniqueConstraint("user_low_id", "user_high_id", name="uq_friend_requests_pair"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_low_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    user_high_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    requester_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

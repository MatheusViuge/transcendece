"""add friendship consent and privacy-safe friend codes

Revision ID: 0007_friendship_privacy
Revises: 0006_user_interaction
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_friendship_privacy"
down_revision = "0006_user_interaction"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("friend_code", sa.String(length=11), nullable=True))
    op.execute(
        """
        UPDATE usuarios
        SET friend_code = upper(
            substr(md5(random()::text || clock_timestamp()::text), 1, 5)
            || '-'
            || substr(md5(random()::text || clock_timestamp()::text), 1, 5)
        )
        WHERE friend_code IS NULL
        """
    )
    op.alter_column("usuarios", "friend_code", existing_type=sa.String(length=11), nullable=False)
    op.create_index("ix_usuarios_friend_code", "usuarios", ["friend_code"], unique=True)

    op.create_table(
        "friend_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_low_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_high_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("user_low_id < user_high_id", name="ck_friend_requests_order"),
        sa.CheckConstraint(
            "requester_id = user_low_id OR requester_id = user_high_id",
            name="ck_friend_requests_requester_participant",
        ),
        sa.UniqueConstraint("user_low_id", "user_high_id", name="uq_friend_requests_pair"),
    )
    op.create_index("ix_friend_requests_user_low_id", "friend_requests", ["user_low_id"])
    op.create_index("ix_friend_requests_user_high_id", "friend_requests", ["user_high_id"])
    op.create_index("ix_friend_requests_requester_id", "friend_requests", ["requester_id"])


def downgrade() -> None:
    op.drop_index("ix_friend_requests_requester_id", table_name="friend_requests")
    op.drop_index("ix_friend_requests_user_high_id", table_name="friend_requests")
    op.drop_index("ix_friend_requests_user_low_id", table_name="friend_requests")
    op.drop_table("friend_requests")
    op.drop_index("ix_usuarios_friend_code", table_name="usuarios")
    op.drop_column("usuarios", "friend_code")

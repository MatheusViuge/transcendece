"""add standard user management

Revision ID: 0005_user_management
Revises: 0004_file_upload
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_user_management"
down_revision = "0004_file_upload"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("avatar_file_id", sa.Integer(), nullable=True))
    op.add_column("usuarios", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_usuarios_avatar_file_id", "usuarios", ["avatar_file_id"])
    op.create_foreign_key(
        "fk_usuarios_avatar_file_id",
        "usuarios",
        "uploaded_files",
        ["avatar_file_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_table(
        "friendships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_low_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_high_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("user_low_id < user_high_id", name="ck_friendships_order"),
        sa.UniqueConstraint("user_low_id", "user_high_id", name="uq_friendships_pair"),
    )
    op.create_index("ix_friendships_user_low_id", "friendships", ["user_low_id"])
    op.create_index("ix_friendships_user_high_id", "friendships", ["user_high_id"])


def downgrade() -> None:
    op.drop_index("ix_friendships_user_high_id", table_name="friendships")
    op.drop_index("ix_friendships_user_low_id", table_name="friendships")
    op.drop_table("friendships")
    op.drop_constraint("fk_usuarios_avatar_file_id", "usuarios", type_="foreignkey")
    op.drop_index("ix_usuarios_avatar_file_id", table_name="usuarios")
    op.drop_column("usuarios", "last_seen_at")
    op.drop_column("usuarios", "avatar_file_id")

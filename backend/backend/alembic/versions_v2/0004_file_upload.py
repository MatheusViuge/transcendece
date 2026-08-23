"""add uploaded file metadata

Revision ID: 0004_file_upload
Revises: 0003_rbac_user_state
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_file_upload"
down_revision = "0003_rbac_user_state"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("storage_name", sa.String(length=80), nullable=False, unique=True),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=50), nullable=False, server_default="general"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_uploaded_files_owner_id", "uploaded_files", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_uploaded_files_owner_id", table_name="uploaded_files")
    op.drop_table("uploaded_files")

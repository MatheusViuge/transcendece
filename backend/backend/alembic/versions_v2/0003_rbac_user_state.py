"""add RBAC user state and role constraint

Revision ID: 0003_rbac_user_state
Revises: 0002_public_api_keys
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_rbac_user_state"
down_revision = "0002_public_api_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_check_constraint(
        "ck_usuarios_tipo_usuario",
        "usuarios",
        "tipo_usuario IN ('aluno', 'instrutor', 'admin')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_usuarios_tipo_usuario", "usuarios", type_="check")
    op.drop_column("usuarios", "is_active")

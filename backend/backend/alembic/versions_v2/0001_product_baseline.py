"""product schema baseline

Revision ID: 0001_product_baseline
Revises:
Create Date: 2026-08-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_product_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=45), nullable=False),
        sa.Column("sobrenome", sa.String(length=45), nullable=False),
        sa.Column("data_nascimento", sa.Date(), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("tipo_usuario", sa.String(length=20), nullable=False, server_default="aluno"),
        sa.Column("data_cadastro", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("ultimo_login", sa.DateTime(), nullable=True),
        sa.Column("ultima_atualizacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )

    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_categorias_nome"),
    )

    op.create_table(
        "especialidade",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_especialidade_nome"),
    )

    op.create_table(
        "niveis",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("descricao", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("descricao", name="uq_niveis_descricao"),
    )

    op.create_table(
        "instrutores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("especialidade", sa.Integer(), nullable=False),
        sa.Column("biografia", sa.String(length=300), nullable=True),
        sa.Column("data_cadastro", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("ultima_alteracao", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["especialidade"], ["especialidade.id"]),
        sa.ForeignKeyConstraint(["id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cursos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url_image", sa.String(length=200), nullable=True),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("preco", sa.Float(), nullable=False),
        sa.Column("carga_horaria", sa.Integer(), nullable=False),
        sa.Column("nivel_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("instrutor_id", sa.Integer(), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ultima_atualizacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["instrutor_id"], ["instrutores.id"]),
        sa.ForeignKeyConstraint(["nivel_id"], ["niveis.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "modulos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ultima_atualizacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "aulas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("ordem_aula", sa.Integer(), nullable=False),
        sa.Column("duracao_minutos", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("subtitulo", sa.Text(), nullable=True),
        sa.Column("modulo_id", sa.Integer(), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ultima_atualizacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["modulo_id"], ["modulos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "matriculas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("data_matricula", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("status_matricula", sa.String(length=12), nullable=False, server_default="ativa"),
        sa.Column("data_conclusao", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["aluno_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("aluno_id", "curso_id", name="uq_matriculas_aluno_curso"),
    )

    op.create_table(
        "desempenho",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("matricula_id", sa.Integer(), nullable=False),
        sa.Column("nota", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.String(length=500), nullable=True),
        sa.Column("data_avaliacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["matricula_id"], ["matriculas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "avaliacao_curso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nota", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("nota >= 1 AND nota <= 5", name="check_nota_range"),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "curso_id", name="uc_usuario_curso_avaliacao"),
    )

    op.create_table(
        "progresso_aulas",
        sa.Column("matricula_id", sa.Integer(), nullable=False),
        sa.Column("aula_id", sa.Integer(), nullable=False),
        sa.Column("progresso_percentual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("concluido", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("data_conclusao", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["aula_id"], ["aulas.id"]),
        sa.ForeignKeyConstraint(["matricula_id"], ["matriculas.id"]),
        sa.PrimaryKeyConstraint("matricula_id", "aula_id"),
    )

    op.create_table(
        "certificados",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("matricula_id", sa.Integer(), nullable=False),
        sa.Column("data_conclusao", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_emissao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["matricula_id"], ["matriculas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("matricula_id", name="uq_certificados_matricula_id"),
    )


def downgrade() -> None:
    op.drop_table("certificados")
    op.drop_table("progresso_aulas")
    op.drop_table("avaliacao_curso")
    op.drop_table("desempenho")
    op.drop_table("matriculas")
    op.drop_table("aulas")
    op.drop_table("modulos")
    op.drop_table("cursos")
    op.drop_table("instrutores")
    op.drop_table("niveis")
    op.drop_table("especialidade")
    op.drop_table("categorias")
    op.drop_table("usuarios")

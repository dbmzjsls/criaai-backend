"""create pgvector extension and product_embeddings table

Revision ID: 002
Revises: 001_initial_schema
Create Date: 2026-05-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 启用 pgvector 扩展
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 创建产品向量嵌入表
    op.create_table(
        "product_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.String(64), nullable=False),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=False),
        sa.Column("extra_data", sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        comment="产品向量嵌入表 - 巴西电商数据集"
    )
    op.create_index("ix_product_embeddings_product_id", "product_embeddings", ["product_id"])


def downgrade() -> None:
    op.drop_table("product_embeddings")
    op.execute("DROP EXTENSION IF EXISTS vector")

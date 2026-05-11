"""platform_rules + violation_logs tables

Revision ID: 003
Revises: 002
Create Date: 2026-05-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("rule_type", sa.String(20), nullable=False, server_default="keyword"),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False, server_default="block"),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("pattern", sa.Text(), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        comment="平台规范规则表"
    )
    op.create_index("ix_platform_rules_platform", "platform_rules", ["platform"])
    op.create_index("ix_platform_rules_active", "platform_rules", ["is_active"])

    op.create_table(
        "violation_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("rule_type", sa.String(20), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("matched_keyword", sa.String(255), nullable=True),
        sa.Column("content_preview", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(10), nullable=False),
        sa.Column("source_path", sa.String(500), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["rule_id"], ["platform_rules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        comment="违规日志表"
    )
    op.create_index("ix_violation_logs_created", "violation_logs", ["created_at"])
    op.create_index("ix_violation_logs_platform", "violation_logs", ["platform"])


def downgrade() -> None:
    op.drop_table("violation_logs")
    op.drop_table("platform_rules")

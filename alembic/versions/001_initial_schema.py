"""初始数据库表结构

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-03-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('subscription_tier', sa.String(20), server_default='free')
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # 创建产品档案表
    op.create_table(
        'product_profiles',
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_name', sa.String(200), nullable=False),
        sa.Column('product_type', sa.String(100)),
        sa.Column('product_features', sa.Text),
        sa.Column('target_audience', sa.Text),
        sa.Column('target_market', sa.String(50)),
        sa.Column('platform_channels', postgresql.ARRAY(sa.Text)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )

    # 创建内容资产表
    op.create_table(
        'content_assets',
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True)),
        sa.Column('asset_type', sa.String(20), nullable=False),
        sa.Column('content_data', postgresql.JSONB, nullable=False),
        sa.Column('asset_metadata', postgresql.JSONB),
        sa.Column('version', sa.Integer, server_default='1'),
        sa.Column('parent_asset_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profile_id'], ['product_profiles.profile_id']),
        sa.ForeignKeyConstraint(['parent_asset_id'], ['content_assets.asset_id'])
    )

    # 创建批量生成任务表
    op.create_table(
        'batch_generation_tasks',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True)),
        sa.Column('task_status', sa.String(20), server_default='pending'),
        sa.Column('task_config', postgresql.JSONB, nullable=False),
        sa.Column('progress', sa.Integer, server_default='0'),
        sa.Column('result_asset_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['profile_id'], ['product_profiles.profile_id'])
    )

    # 创建素材库表
    op.create_table(
        'media_library',
        sa.Column('media_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('media_type', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String)),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )


def downgrade() -> None:
    op.drop_table('media_library')
    op.drop_table('batch_generation_tasks')
    op.drop_table('content_assets')
    op.drop_table('product_profiles')
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_username', 'users')
    op.drop_table('users')

"""
资产数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
from core.database import Base


class ContentAsset(Base):
    """内容资产表"""
    __tablename__ = "content_assets"

    asset_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('product_profiles.profile_id'))
    asset_type = Column(String(20), nullable=False)  # 'copywriting', 'image', 'video'
    content_data = Column(JSON, nullable=False)
    asset_metadata = Column(JSON)
    version = Column(Integer, default=1)
    parent_asset_id = Column(UUID(as_uuid=True), ForeignKey('content_assets.asset_id'))
    created_at = Column(DateTime, default=datetime.utcnow)


class BatchGenerationTask(Base):
    """批量生成任务表"""
    __tablename__ = "batch_generation_tasks"

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    profile_id = Column(UUID(as_uuid=True), ForeignKey('product_profiles.profile_id'))
    task_status = Column(String(20), default='pending')  # 'pending', 'running', 'completed', 'failed'
    task_config = Column(JSON, nullable=False)
    progress = Column(Integer, default=0)
    result_asset_ids = Column(ARRAY(UUID(as_uuid=True)))
    created_at = Column(DateTime, default=datetime.utcnow)


class MediaLibrary(Base):
    """素材库表"""
    __tablename__ = "media_library"

    media_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    media_type = Column(String(20), nullable=False)  # 'image', 'video', 'audio'
    file_path = Column(String(500), nullable=False)
    tags = Column(ARRAY(String))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

"""
素材库 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class MediaUploadResponse(BaseModel):
    """素材上传响应"""
    media_id: UUID
    user_id: UUID
    media_type: str
    file_path: str
    file_url: str
    tags: Optional[List[str]] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """素材列表响应"""
    media_id: UUID
    media_type: str
    file_url: str
    tags: Optional[List[str]] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class MediaDeleteResponse(BaseModel):
    """素材删除响应"""
    success: bool
    message: str

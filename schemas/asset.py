"""
资产 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ContentAssetBase(BaseModel):
    """内容资产基础模型"""
    asset_type: str = Field(..., pattern="^(copywriting|image|video)$")
    content_data: Dict[str, Any]
    asset_metadata: Optional[Dict[str, Any]] = None


class ContentAssetCreate(ContentAssetBase):
    """内容资产创建模型"""
    profile_id: Optional[UUID] = None
    parent_asset_id: Optional[UUID] = None


class ContentAssetResponse(ContentAssetBase):
    """内容资产响应模型"""
    asset_id: UUID
    user_id: UUID
    profile_id: Optional[UUID]
    version: int
    parent_asset_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True



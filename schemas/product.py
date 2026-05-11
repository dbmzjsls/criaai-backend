"""
产品 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ProductProfileBase(BaseModel):
    """产品档案基础模型"""
    product_name: str = Field(..., max_length=200)
    product_type: Optional[str] = None
    product_features: Optional[str] = None
    target_audience: Optional[str] = None
    target_market: Optional[str] = None
    platform_channels: Optional[List[str]] = None


class ProductProfileCreate(ProductProfileBase):
    """产品档案创建模型"""
    pass


class ProductProfileUpdate(ProductProfileBase):
    """产品档案更新模型"""
    product_name: Optional[str] = None


class ProductProfileResponse(ProductProfileBase):
    """产品档案响应模型"""
    profile_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

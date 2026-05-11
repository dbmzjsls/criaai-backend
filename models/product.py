"""
产品数据模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database import Base


class ProductProfile(Base):
    """产品档案表"""
    __tablename__ = "product_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(100))
    product_features = Column(Text)
    target_audience = Column(Text)
    target_market = Column(String(50))
    platform_channels = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)

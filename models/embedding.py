"""
向量嵌入数据模型
使用 pgvector 存储产品向量嵌入
"""
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSON

from core.database import Base


class ProductEmbedding(Base):
    """产品向量嵌入表"""

    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(64), nullable=False, comment="巴西电商数据集中的 product_id")
    category = Column(String(128), nullable=True, comment="产品分类（英文）")
    text = Column(Text, nullable=False, comment="用于生成嵌入的原文（产品名+分类）")
    embedding = Column(Vector(1024), nullable=False, comment="嵌入向量 (1024维)")
    extra_data = Column(JSON, nullable=True, comment="原始产品元数据")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_product_embeddings_product_id", "product_id"),
        {"comment": "产品向量嵌入表 - 巴西电商数据集"}
    )

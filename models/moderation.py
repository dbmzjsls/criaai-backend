"""
内容审核数据模型
平台规范规则 + 违规日志
"""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class PlatformRule(Base):
    """平台规范规则表"""

    __tablename__ = "platform_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(20), nullable=False, comment="平台: amazon, shopee, lazada 等")
    rule_type = Column(
        String(20), nullable=False, default="keyword",
        comment="规则类型: keyword, regex, semantic, image"
    )
    category = Column(String(50), nullable=False, comment="违规分类: 违禁商品, 虚假宣传, 侵权 等")
    severity = Column(
        String(10), nullable=False, default="block",
        comment="严重级别: block (拦截), warn (警告)"
    )
    keywords = Column(Text, nullable=True, comment="关键词列表 (JSON 数组字符串)")
    pattern = Column(Text, nullable=True, comment="正则表达式 (regex 规则用)")
    description = Column(String(500), nullable=True, comment="规则说明")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_platform_rules_platform", "platform"),
        Index("ix_platform_rules_active", "is_active"),
        {"comment": "平台规范规则表"}
    )


class ViolationLog(Base):
    """违规日志表"""

    __tablename__ = "violation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("platform_rules.id", ondelete="SET NULL"), nullable=True)
    platform = Column(String(20), nullable=False, comment="触发平台")
    rule_type = Column(String(20), nullable=False, comment="规则类型")
    category = Column(String(50), nullable=False, comment="违规分类")
    severity = Column(String(10), nullable=False, comment="严重级别")
    matched_keyword = Column(String(255), nullable=True, comment="命中的关键词")
    content_preview = Column(Text, nullable=True, comment="违规内容预览(前500字)")
    source_type = Column(String(10), nullable=False, comment="来源: text / image")
    source_path = Column(String(500), nullable=True, comment="图片路径 (image 类型时)")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_violation_logs_created", "created_at"),
        Index("ix_violation_logs_platform", "platform"),
        {"comment": "违规日志表"}
    )

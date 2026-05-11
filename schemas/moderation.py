"""
审核相关 Pydantic 模式
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ──── 规则 ────

class RuleCreate(BaseModel):
    platform: str = Field(..., min_length=1, max_length=20)
    rule_type: str = Field(default="keyword", pattern="^(keyword|regex|semantic|image)$")
    category: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(default="block", pattern="^(block|warn)$")
    keywords: list[str] | None = None
    pattern: str | None = None
    description: str | None = Field(None, max_length=500)
    is_active: bool = True


class RuleUpdate(BaseModel):
    platform: Optional[str] = Field(None, min_length=1, max_length=20)
    rule_type: Optional[str] = Field(None, pattern="^(keyword|regex|semantic|image)$")
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    severity: Optional[str] = Field(None, pattern="^(block|warn)$")
    keywords: Optional[list[str]] = None
    pattern: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class RuleResponse(BaseModel):
    id: int
    platform: str
    rule_type: str
    category: str
    severity: str
    keywords: list[str] | None = None
    pattern: str | None = None
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RuleListResponse(BaseModel):
    rules: list[RuleResponse]
    total: int


# ──── 测试 ────

class TestRuleRequest(BaseModel):
    text: str = Field(..., min_length=1, description="要测试的文本")
    platform: str = Field(default="amazon")
    rule_types: list[str] = Field(default=["keyword"])


class Violation(BaseModel):
    rule_id: int | None = None
    platform: str
    rule_type: str
    category: str
    severity: str
    matched_keyword: str | None = None
    description: str | None = None


class TestRuleResponse(BaseModel):
    passed: bool
    violations: list[Violation] = []
    source_type: str = "text"


# ──── 违规日志 ────

class ViolationLogResponse(BaseModel):
    id: int
    rule_id: int | None = None
    platform: str
    rule_type: str
    category: str
    severity: str
    matched_keyword: str | None = None
    content_preview: str | None = None
    source_type: str
    source_path: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ViolationListResponse(BaseModel):
    violations: list[ViolationLogResponse]
    total: int


# ──── 统计 ────

class ModerationStatistics(BaseModel):
    total_violations: int
    violations_today: int
    by_platform: dict[str, int]
    by_category: dict[str, int]
    by_severity: dict[str, int]

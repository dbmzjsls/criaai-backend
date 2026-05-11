"""
内容审核 API 路由
规则管理 + 测试 + 违规日志 + 统计
"""
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from models.moderation import PlatformRule, ViolationLog
from schemas.moderation import (
    RuleCreate, RuleUpdate, RuleResponse, RuleListResponse,
    TestRuleRequest, TestRuleResponse, Violation,
    ViolationLogResponse, ViolationListResponse,
    ModerationStatistics,
)
from services.rule_engine import rule_engine

router = APIRouter(prefix="/api/v1/moderation", tags=["内容审核"])


def _rule_to_response(rule: PlatformRule) -> RuleResponse:
    """ORM → Pydantic"""
    keywords = None
    if rule.keywords:
        try:
            keywords = json.loads(rule.keywords)
        except (json.JSONDecodeError, TypeError):
            keywords = []
    return RuleResponse(
        id=rule.id,
        platform=rule.platform,
        rule_type=rule.rule_type,
        category=rule.category,
        severity=rule.severity,
        keywords=keywords,
        pattern=rule.pattern,
        description=rule.description,
        is_active=rule.is_active,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


# ──── 规则测试 ────

@router.post("/rules/test", response_model=TestRuleResponse)
def test_rules(req: TestRuleRequest, db: Session = Depends(get_db)):
    """测试规则（不记录日志），用于验证规则效果"""
    result = rule_engine.evaluate(
        db=db,
        platform=req.platform.lower(),
        content_text=req.text,
        source_type="text",
        log_violations=False,  # 测试不记日志
    )
    return TestRuleResponse(
        passed=result.passed,
        violations=result.violations,
        source_type=result.source_type,
    )


# ──── 规则 CRUD ────

@router.get("/rules", response_model=RuleListResponse)
def list_rules(
    platform: Optional[str] = Query(None),
    rule_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """获取规则列表，支持筛选"""
    query = db.query(PlatformRule)
    if platform:
        query = query.filter(PlatformRule.platform == platform.lower())
    if rule_type:
        query = query.filter(PlatformRule.rule_type == rule_type)
    if is_active is not None:
        query = query.filter(PlatformRule.is_active == is_active)

    total = query.count()
    rules = query.order_by(PlatformRule.id).offset(skip).limit(limit).all()
    return RuleListResponse(
        rules=[_rule_to_response(r) for r in rules],
        total=total,
    )


@router.post("/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(req: RuleCreate, db: Session = Depends(get_db)):
    """创建新规则"""
    rule = PlatformRule(
        platform=req.platform.lower(),
        rule_type=req.rule_type,
        category=req.category,
        severity=req.severity,
        keywords=json.dumps(req.keywords, ensure_ascii=False) if req.keywords else None,
        pattern=req.pattern,
        description=req.description,
        is_active=req.is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _rule_to_response(rule)


@router.get("/rules/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """获取单个规则"""
    rule = db.query(PlatformRule).filter(PlatformRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return _rule_to_response(rule)


@router.put("/rules/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, req: RuleUpdate, db: Session = Depends(get_db)):
    """更新规则"""
    rule = db.query(PlatformRule).filter(PlatformRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    update_data = req.model_dump(exclude_unset=True)
    if "keywords" in update_data and update_data["keywords"] is not None:
        update_data["keywords"] = json.dumps(update_data["keywords"], ensure_ascii=False)

    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    return _rule_to_response(rule)


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """软删除规则（设为非活跃）"""
    rule = db.query(PlatformRule).filter(PlatformRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    rule.is_active = False
    db.commit()
    return {"success": True, "message": f"规则 #{rule_id} 已停用"}


# ──── 违规日志 ────

@router.get("/violations", response_model=ViolationListResponse)
def list_violations(
    platform: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, description="开始日期 ISO 格式"),
    to_date: Optional[str] = Query(None, description="结束日期 ISO 格式"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """查询违规日志"""
    query = db.query(ViolationLog)
    if platform:
        query = query.filter(ViolationLog.platform == platform.lower())
    if severity:
        query = query.filter(ViolationLog.severity == severity)
    if source_type:
        query = query.filter(ViolationLog.source_type == source_type)
    if from_date:
        query = query.filter(ViolationLog.created_at >= from_date)
    if to_date:
        query = query.filter(ViolationLog.created_at <= to_date)

    total = query.count()
    logs = query.order_by(ViolationLog.created_at.desc()).offset(skip).limit(limit).all()

    return ViolationListResponse(
        violations=[
            ViolationLogResponse(
                id=log.id,
                rule_id=log.rule_id,
                platform=log.platform,
                rule_type=log.rule_type,
                category=log.category,
                severity=log.severity,
                matched_keyword=log.matched_keyword,
                content_preview=log.content_preview,
                source_type=log.source_type,
                source_path=log.source_path,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=total,
    )


# ──── 统计 ────

@router.get("/statistics", response_model=ModerationStatistics)
def get_statistics(db: Session = Depends(get_db)):
    """获取审核统计数据"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total = db.query(ViolationLog).count()
    today = db.query(ViolationLog).filter(ViolationLog.created_at >= today_start).count()

    # 按平台统计
    plat_rows = (
        db.query(ViolationLog.platform, db.func.count(ViolationLog.id))
        .group_by(ViolationLog.platform).all()
    )
    by_platform = {row[0]: row[1] for row in plat_rows}

    # 按分类统计
    cat_rows = (
        db.query(ViolationLog.category, db.func.count(ViolationLog.id))
        .group_by(ViolationLog.category).all()
    )
    by_category = {row[0]: row[1] for row in cat_rows}

    # 按严重级别统计
    sev_rows = (
        db.query(ViolationLog.severity, db.func.count(ViolationLog.id))
        .group_by(ViolationLog.severity).all()
    )
    by_severity = {row[0]: row[1] for row in sev_rows}

    return ModerationStatistics(
        total_violations=total,
        violations_today=today,
        by_platform=by_platform,
        by_category=by_category,
        by_severity=by_severity,
    )

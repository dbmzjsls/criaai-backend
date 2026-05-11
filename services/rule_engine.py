"""
多规则引擎
策略模式：RuleChecker 抽象基类 + 可插拔检查器
"""
import json
from abc import ABC, abstractmethod
from typing import List, Dict

from sqlalchemy.orm import Session

from models.moderation import PlatformRule, ViolationLog
from schemas.moderation import Violation


class RuleChecker(ABC):
    """规则检查器抽象基类"""

    @abstractmethod
    def check(self, text: str, rules: list[PlatformRule]) -> list[Violation]:
        """检查文本是否命中规则，返回违规列表"""
        ...


class KeywordChecker(RuleChecker):
    """关键词黑名单检查器"""

    def check(self, text: str, rules: list[PlatformRule]) -> list[Violation]:
        violations = []
        text_lower = text.lower()

        for rule in rules:
            if not rule.keywords:
                continue
            try:
                keywords = json.loads(rule.keywords)
            except (json.JSONDecodeError, TypeError):
                continue

            for kw in keywords:
                if not kw:
                    continue
                if kw.lower() in text_lower:
                    violations.append(Violation(
                        rule_id=rule.id,
                        platform=rule.platform,
                        rule_type=rule.rule_type,
                        category=rule.category,
                        severity=rule.severity,
                        matched_keyword=kw,
                        description=rule.description or f"命中关键词: {kw}"
                    ))

        return violations


class RuleEngine:
    """规则引擎：注册检查器 + 执行评估"""

    def __init__(self):
        self.checkers: Dict[str, RuleChecker] = {
            "keyword": KeywordChecker(),
            # 未来扩展:
            # "regex": RegexChecker(),
            # "semantic": SemanticChecker(),
            # "image": ImageChecker(),
        }

    def register_checker(self, rule_type: str, checker: RuleChecker):
        """注册新的规则检查器"""
        self.checkers[rule_type] = checker

    def get_active_rules(
        self, db: Session, platform: str, rule_types: list[str] | None = None
    ) -> list[PlatformRule]:
        """获取指定平台的活跃规则"""
        query = db.query(PlatformRule).filter(
            PlatformRule.platform == platform,
            PlatformRule.is_active == True
        )
        if rule_types:
            query = query.filter(PlatformRule.rule_type.in_(rule_types))
        return query.all()

    def evaluate(
        self,
        db: Session,
        platform: str,
        content_text: str,
        source_type: str = "text",
        user_id: str | None = None,
        log_violations: bool = True,
    ) -> "ModerationResult":
        """
        评估内容是否违规

        Args:
            db: 数据库会话
            platform: 平台标识 (amazon, shopee)
            content_text: 待检查的文本内容
            source_type: 'text' 或 'image'
            user_id: 用户 ID (用于日志)
            log_violations: 是否记录违规日志

        Returns:
            ModerationResult
        """
        # 确定要执行的规则类型
        rule_types_to_check = list(self.checkers.keys())
        if source_type == "image":
            rule_types_to_check = [rt for rt in rule_types_to_check if rt in ("keyword", "image")]

        # 获取规则
        rules = self.get_active_rules(db, platform, rule_types_to_check)

        # 按 rule_type 分组
        rules_by_type: Dict[str, list[PlatformRule]] = {}
        for rule in rules:
            rules_by_type.setdefault(rule.rule_type, []).append(rule)

        # 执行检查
        all_violations: list[Violation] = []
        for rule_type, rules_of_type in rules_by_type.items():
            checker = self.checkers.get(rule_type)
            if checker:
                violations = checker.check(content_text, rules_of_type)
                all_violations.extend(violations)

        # 判断是否通过
        blocking_violations = [v for v in all_violations if v.severity == "block"]
        passed = len(blocking_violations) == 0

        # 记录日志
        if log_violations and all_violations:
            self._log_violations(db, all_violations, content_text, source_type, user_id)

        return ModerationResult(
            passed=passed,
            violations=all_violations,
            source_type=source_type,
        )

    def _log_violations(
        self,
        db: Session,
        violations: list[Violation],
        content_text: str,
        source_type: str,
        user_id: str | None,
    ):
        """将违规记录写入数据库"""
        content_preview = content_text[:500] if len(content_text) > 500 else content_text
        source_path = None  # image 类型由 interceptor 设置

        for v in violations:
            log = ViolationLog(
                rule_id=v.rule_id,
                platform=v.platform,
                rule_type=v.rule_type,
                category=v.category,
                severity=v.severity,
                matched_keyword=v.matched_keyword,
                content_preview=content_preview,
                source_type=source_type,
                source_path=source_path,
                user_id=user_id,
            )
            db.add(log)

        db.commit()


class ModerationResult:
    """审核结果"""

    def __init__(self, passed: bool, violations: list[Violation], source_type: str):
        self.passed = passed
        self.violations = violations
        self.source_type = source_type


# 全局单例
rule_engine = RuleEngine()

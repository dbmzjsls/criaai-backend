"""
多规则引擎
策略模式：RuleChecker 抽象基类 + 可插拔检查器
"""
import json
import re
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
    """
    关键词黑名单检查器 - 智能词边界匹配

    策略：
      - ASCII 关键词：使用 \\b 词边界，防止 "drug" 误伤 "drugstore"
      - CJK 关键词（单字）：跳过 —— 单字杀伤力太大（"核"→"核心"）
      - CJK 关键词（多字）：子串匹配，中文天然不易误伤复合词
      - 含空格/符号的变体（"d r u g"）：直接子串匹配
    """

    # 预编译常见绕词变体（空格/符号分隔），不走词边界
    _EVASION_PATTERN = re.compile(r'\s+|\.+|-+')

    @staticmethod
    def _is_cjk_single_char(kw: str) -> bool:
        """判断是否为单独一个 CJK 字符（不含任何其他字符）"""
        if len(kw) != 1:
            return False
        cp = ord(kw)
        return (
            (0x4E00 <= cp <= 0x9FFF)   # CJK Unified
            or (0x3400 <= cp <= 0x4DBF)  # CJK Ext-A
            or (0xF900 <= cp <= 0xFAFF)  # CJK Compat
        )

    @staticmethod
    def _is_pure_ascii(kw: str) -> bool:
        """判断关键词是否纯 ASCII（字母/数字）"""
        return kw.isascii() and all(c.isalnum() or c in ' ' for c in kw)

    def _kw_matches(self, kw: str, text_lower: str) -> bool:
        """判断关键词是否命中文本"""
        kw_lower = kw.lower()

        # 单字 CJK → 跳过（杀伤力太大，如 "核"→"核心"、"毒"→"病毒"）
        if self._is_cjk_single_char(kw_lower):
            return False

        # 含空格/符号的绕词变体 → 规范化后子串匹配（"d r u g" → "drug"）
        if ' ' in kw_lower or '.' in kw_lower or '-' in kw_lower:
            normalized = self._EVASION_PATTERN.sub('', kw_lower)
            text_normalized = self._EVASION_PATTERN.sub('', text_lower)
            return normalized in text_normalized

        # 纯 ASCII 关键词 → 词边界匹配（\bdrug\b 不匹配 drugstore）
        if self._is_pure_ascii(kw_lower):
            pattern = r'(?<![a-z])' + re.escape(kw_lower) + r'(?![a-z])'
            return bool(re.search(pattern, text_lower))

        # 中文多字及其他 → 子串匹配（中文无英文式复合词问题）
        return kw_lower in text_lower

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
                if self._kw_matches(kw, text_lower):
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

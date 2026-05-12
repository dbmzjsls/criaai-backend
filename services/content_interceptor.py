"""
内容拦截器
协调 OCR + 规则引擎，在内容返回前进行审核
"""
import re
import logging
from sqlalchemy.orm import Session

from services.rule_engine import rule_engine, ModerationResult
from services.ocr_service import ocr_service


class ContentInterceptor:
    """内容拦截器：统一的内容审核入口"""

    def __init__(self):
        self.rule_engine = rule_engine
        self.ocr = ocr_service

    def intercept_text(
        self,
        db: Session,
        platform: str,
        text_content: str,
        user_id: str | None = None,
    ) -> ModerationResult:
        return self.rule_engine.evaluate(
            db=db,
            platform=platform.lower(),
            content_text=text_content,
            source_type="text",
            user_id=user_id,
        )

    def intercept_image(
        self,
        db: Session,
        platform: str,
        image_path: str,
        user_id: str | None = None,
    ) -> ModerationResult:
        try:
            ocr_text = self.ocr.extract_text(image_path)
        except Exception as e:
            logging.getLogger(__name__).warning(f"OCR failed, allowing content through: {e}")
            return ModerationResult(passed=True, violations=[], source_type="image")

        if not ocr_text or not ocr_text.strip():
            return ModerationResult(passed=True, violations=[], source_type="image")

        return self.rule_engine.evaluate(
            db=db,
            platform=platform.lower(),
            content_text=ocr_text,
            source_type="image",
            user_id=user_id,
        )

    def auto_censor(
        self,
        text: str,
        violations: list,
    ) -> tuple[str, int]:
        """
        自动净化：将命中关键词替换为 ***

        Args:
            text: 原始文本
            violations: 违规列表

        Returns:
            (净化后文本, 替换次数)
        """
        if not violations:
            return text, 0

        # 按关键词长度降序排列，避免短词先替换破坏长词
        keywords = sorted(
            set(v.matched_keyword for v in violations if v.matched_keyword),
            key=len, reverse=True,
        )

        result = text
        count = 0
        for kw in keywords:
            # 大小写不敏感替换
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            new_result, n = pattern.subn("***", result)
            if n > 0:
                count += n
                result = new_result

        return result, count

    def intercept_output(
        self,
        db: Session,
        platform: str,
        generated_content: str,
        user_id: str | None = None,
        max_censor_ratio: float = 0.3,
    ) -> dict:
        """
        AI 输出审核：自动净化 + 返回状态，不直接拦截

        Args:
            db: 数据库会话
            platform: 平台标识
            generated_content: AI 生成的文本
            user_id: 用户 ID
            max_censor_ratio: 净化比例超过此值建议重试

        Returns:
            {
                "content": str,          # 最终文本（可能已净化）
                "censored_count": int,   # 替换次数
                "needs_retry": bool,     # 是否需要重试
                "blocked_keywords": list # 命中的关键词
            }
        """
        result = self.intercept_text(
            db=db, platform=platform,
            text_content=generated_content, user_id=user_id,
        )

        if result.passed:
            return {
                "content": generated_content,
                "censored_count": 0,
                "needs_retry": False,
                "blocked_keywords": [],
            }

        # 提取 block 级别的违规词
        blocked = [v for v in result.violations if v.severity == "block"]
        blocked_kw = [v.matched_keyword for v in blocked if v.matched_keyword]

        # 自动净化
        cleaned, count = self.auto_censor(generated_content, result.violations)

        # 如果净化比例过高（>max_censor_ratio 的文本被替换），建议重试
        total_chars = len(generated_content)
        censored_chars = count * 3  # "***" = 3 chars per replacement
        needs_retry = total_chars > 0 and (censored_chars / total_chars) > max_censor_ratio

        return {
            "content": cleaned,
            "censored_count": count,
            "needs_retry": needs_retry,
            "blocked_keywords": blocked_kw,
        }


# 全局单例
content_interceptor = ContentInterceptor()

"""
内容拦截器
协调 OCR + 规则引擎，在内容返回前进行审核
"""
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
        """
        拦截文本内容

        Args:
            db: 数据库会话
            platform: 平台标识
            text_content: 文本内容
            user_id: 用户 ID

        Returns:
            ModerationResult
        """
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
        """
        拦截图片内容：OCR 提取文字 → 规则引擎检查

        Args:
            db: 数据库会话
            platform: 平台标识
            image_path: 图片文件路径
            user_id: 用户 ID

        Returns:
            ModerationResult (source_type="image")
        """
        # OCR 失败时 fail-open：不阻塞
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


# 全局单例
content_interceptor = ContentInterceptor()

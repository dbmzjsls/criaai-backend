"""
文案生成服务模块
使用通义千问（Dashscope OpenAI 兼容端点）生成营销文案
"""
import logging
import json
from http import HTTPStatus
from typing import Optional, Dict, Any, List

import requests
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from models.product import ProductProfile
from core.config import settings
from services.asset_service import asset_service

logger = logging.getLogger(__name__)


class CopywritingService:
    """文案生成服务"""

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = "qwen3.5-flash"

    def generate_text(self, prompt: str) -> str:
        """
        纯文本生成（无需 product_id），供 pipeline 等场景调用

        Args:
            prompt: 完整的提示词

        Returns:
            生成的文本内容
        """
        return self._call_dashscope_api(prompt)

    def generate_copywriting(
        self,
        db: Session,
        product_id: str,
        language: str = "英语",
        style: str = "专业",
        platform: str = "Amazon",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成营销文案

        Args:
            db: 数据库会话
            product_id: 产品ID
            language: 目标语言
            style: 文案风格
            platform: 目标平台
            user_id: 用户ID（可选）

        Returns:
            生成的文案内容（包含 asset_id）

        Raises:
            ValueError: 产品不存在或生成失败
        """
        # 查询产品信息
        product = db.query(ProductProfile).filter(
            ProductProfile.profile_id == product_id
        ).first()

        if not product:
            raise ValueError("产品不存在")

        # 构建 Prompt
        prompt = self._build_prompt(
            product=product,
            language=language,
            style=style,
            platform=platform
        )

        # 调用通义千问 API
        try:
            response = self._call_dashscope_api(prompt)

            # 准备返回数据
            result = {
                "content": response,
                "language": language,
                "style": style,
                "platform": platform,
                "product_name": product.product_name
            }

            # 自动保存到资产库
            if user_id:
                try:
                    asset = asset_service.save_asset(
                        db=db,
                        user_id=UUID(user_id),
                        asset_type="copywriting",
                        content_data={
                            "text": response,
                            "language": language,
                            "style": style,
                            "platform": platform,
                            "product_name": product.product_name
                        },
                        profile_id=UUID(product_id),
                        asset_metadata={
                            "word_count": len(response),
                            "generated_at": str(datetime.now())
                        }
                    )
                    result["asset_id"] = str(asset.asset_id)
                except Exception as e:
                    logger.warning(f"保存资产失败: {e}")

            return result
        except Exception as e:
            raise ValueError(f"文案生成失败: {str(e)}")

    def _build_prompt(
        self,
        product: ProductProfile,
        language: str,
        style: str,
        platform: str
    ) -> str:
        """构建文案生成 Prompt"""

        # 语言映射
        language_map = {
            "英语": "English",
            "葡语": "Portuguese",
            "西语": "Spanish",
            "法语": "French",
            "德语": "German",
            "日语": "Japanese"
        }

        # 风格描述
        style_desc = {
            "直白": "直接、简洁、突出产品核心卖点",
            "温馨": "温暖、亲切、注重情感连接",
            "幽默": "轻松、有趣、富有创意",
            "专业": "专业、权威、注重数据和事实"
        }

        target_lang = language_map.get(language, language)
        style_description = style_desc.get(style, style)

        prompt = f"""你是一个专业的跨境电商营销文案专家。

产品信息：
- 名称：{product.product_name}
- 类型：{product.product_type or '未指定'}
- 特点：{product.product_features or '未指定'}
- 目标受众：{product.target_audience or '未指定'}
- 目标市场：{product.target_market or '未指定'}

任务要求：
- 目标语言：{target_lang}
- 文案风格：{style_description}
- 目标平台：{platform}

请生成一段营销文案，要求：
1. 使用{target_lang}语言
2. 符合目标市场的文化习惯
3. 突出产品特点和优势
4. 采用{style}风格
5. 适合{platform}平台的展示格式
6. 包含适当的关键词优化
7. 字数控制在200-300字之间

请直接输出文案内容，不需要额外的说明。"""

        return prompt

    # Dashscope OpenAI 兼容端点
    DASHSCOPE_CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def _call_dashscope_api(self, prompt: str) -> str:
        """
        调用通义千问 API（OpenAI 兼容端点，支持所有模型）

        Args:
            prompt: 输入的提示词

        Returns:
            生成的文案内容

        Raises:
            Exception: API 调用失败时抛出异常
        """
        try:
            logger.info(f"正在调用通义千问 API, Model: {self.model}")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            }

            resp = requests.post(
                self.DASHSCOPE_CHAT_URL,
                headers=headers,
                json=payload,
                timeout=120,
            )

            if resp.status_code != 200:
                error_detail = resp.text[:500]
                try:
                    err = resp.json()
                    error_detail = err.get("message", err.get("error", error_detail))
                except Exception:
                    pass
                raise Exception(
                    f"API 错误 (HTTP {resp.status_code}): {error_detail}"
                )

            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            if not content:
                raise Exception("API 返回内容为空")

            logger.info(f"文案生成成功，长度: {len(content)} 字符")
            return content

        except Exception as e:
            if "API 错误" in str(e) or "API 返回内容为空" in str(e):
                raise
            raise Exception(f"API 调用失败: {type(e).__name__} - {str(e)}")


# 全局服务实例
copywriting_service = CopywritingService()


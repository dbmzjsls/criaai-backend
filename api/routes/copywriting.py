"""
文案生成路由模块
提供营销文案生成 API
"""
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from core.database import get_db
from api.deps import get_current_user
from models.user import User
from services.copywriting_service import copywriting_service
from services.content_interceptor import content_interceptor
from services.vector_service import build_rag_context


router = APIRouter(prefix="/api/v1/copywriting", tags=["文案生成"])

logger = logging.getLogger(__name__)

MAX_RETRY = 1  # 输出审核不通过时最多重试次数


async def _sanitize_output(
    db: Session,
    platform: str,
    content: str,
    keyword: str,
    language_display: str,
    style: str,
    platform_name: str,
    base_prompt: str,
) -> str:
    """
    输出净化 + 智能重试

    1. 先尝试自动净化（违规词 → ***）
    2. 如果净化比例过高（>30%），自动重试并告知 AI 避免哪些词
    3. 重试后仍不合格 → 返回净化版本，不给用户抛错
    """
    for attempt in range(MAX_RETRY + 1):
        result = content_interceptor.intercept_output(
            db=db, platform=platform, generated_content=content,
        )

        # 无违规 → 直接返回
        if result["censored_count"] == 0:
            return content

        # 不需要重试，或已经是最后一次尝试 → 返回净化版
        if not result["needs_retry"] or attempt >= MAX_RETRY:
            if result["censored_count"] > 0:
                logger.info(
                    f"Output auto-censored: {result['censored_count']} occurrences, "
                    f"keywords: {result['blocked_keywords']}"
                )
            return result["content"]

        # 需要重试：告知 AI 避免使用特定词汇
        logger.info(
            f"Output needs retry (attempt {attempt + 1}/{MAX_RETRY}), "
            f"keywords: {result['blocked_keywords']}"
        )
        avoid_list = "、".join(result["blocked_keywords"])
        retry_prompt = (
            f"{base_prompt}\n\n"
            f"【重要提醒】你的上一次回复中包含了不适合在{platform_name}平台展示的词汇。"
            f"请在本次回复中严格避免使用以下词汇或类似表述：{avoid_list}。"
            f"重新生成一份符合{platform_name}平台合规要求的{style}风格{language_display}营销文案。"
        )
        content = await asyncio.to_thread(
            copywriting_service._call_dashscope_api, retry_prompt
        )

    # fallback：返回最后一次净化结果
    return result["content"]


class CopywritingRequest(BaseModel):
    """文案生成请求模型"""
    keyword: str = Field(..., description="产品关键词")
    language: str = Field(default="zh", description="目标语言")
    style: str = Field(default="专业", description="文案风格")
    platform: str = Field(default="Amazon", description="目标平台")


class CopywritingResponse(BaseModel):
    """文案生成响应模型"""
    content: str
    language: str
    style: str
    platform: str
    product_name: str


@router.post("/generate", response_model=CopywritingResponse)
async def generate_copywriting(
    request: CopywritingRequest,
    db: Session = Depends(get_db)
):
    """
    生成营销文案

    Args:
        request: 文案生成请求
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        生成的文案内容

    Raises:
        HTTPException: 生成失败时抛出错误
    """
    try:
        # ====== Step 1: 输入审核（调用模型前） ======
        # 检查用户输入是否命中审核规则，命中则直接拒绝，不浪费 API 调用
        platform_lower = request.platform.lower()
        try:
            input_result = content_interceptor.intercept_text(
                db=db,
                platform=platform_lower,
                text_content=request.keyword,
            )
            if not input_result.passed:
                blocked_keywords = [v.matched_keyword for v in input_result.violations if v.severity == "block"]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "内容违规：检测到禁止使用的敏感词，无法生成相关内容",
                        "message": f"您输入的关键词中包含平台禁止的内容。命中敏感词：{', '.join(blocked_keywords)}。请修改后重试。",
                        "stage": "input_check",
                        "blocked_keywords": blocked_keywords,
                        "violations": [
                            {
                                "category": v.category,
                                "severity": v.severity,
                                "matched_keyword": v.matched_keyword,
                                "description": v.description,
                            }
                            for v in input_result.violations
                            if v.severity == "block"
                        ]
                    }
                )
        except HTTPException:
            raise
        except Exception as e:
            logging.getLogger(__name__).warning(f"Input moderation check failed (allowing through): {e}")

        # ====== Step 2: RAG 向量检索 —— 从巴西电商数据集中召回相似产品 ======
        lang_code_map = {
            "zh": "中文", "en": "英语", "pt": "葡语", "es": "西语",
            "fr": "法语", "de": "德语", "ja": "日语"
        }
        language_display = lang_code_map.get(request.language, request.language)
        try:
            rag_context = await asyncio.to_thread(
                build_rag_context, request.keyword, top_k=5, language=request.language
            )
        except Exception as e:
            logging.getLogger(__name__).warning(f"RAG retrieval failed (continuing without context): {e}")
            rag_context = ""

        # ====== Step 3: 构建 Prompt + 调用 LLM ======
        prompt_parts = [
            "你是一个专业的跨境电商营销文案专家。",
            f"为以下产品生成{language_display}营销文案，风格：{request.style}，平台：{request.platform}",
            f"产品关键词：{request.keyword}",
        ]
        if rag_context:
            prompt_parts.append(f"\n{rag_context}")
            prompt_parts.append("\n请参考以上相似产品的特征和分类，生成更有针对性的营销文案。要求：")
        else:
            prompt_parts.append("\n要求：")
        prompt_parts.extend([
            f"1. 使用{language_display}语言",
            "2. 突出产品特点和优势",
            f"3. 采用{request.style}风格",
            f"4. 适合{request.platform}平台的展示格式",
            "5. 包含适当的关键词优化",
            "6. 字数控制在200-300字之间",
            "7. 直接输出文案内容，不需要额外的说明",
        ])

        prompt = "\n".join(prompt_parts)
        content = await asyncio.to_thread(copywriting_service._call_dashscope_api, prompt)

        # ====== Step 4: 输出审核（自动净化 + 智能重试） ======
        output = await _sanitize_output(
            db=db, platform=platform_lower, content=content,
            keyword=request.keyword, language_display=language_display,
            style=request.style, platform_name=request.platform,
            base_prompt=prompt,
        )

        return CopywritingResponse(
            content=output,
            language=request.language,
            style=request.style,
            platform=request.platform,
            product_name=request.keyword
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文案生成失败: {str(e)}"
        )

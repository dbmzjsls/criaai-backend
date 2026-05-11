"""
图片生成 API 路由
提供营销图片生成和批量生成功能
"""
import logging
import os
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.deps import get_current_user
from models.user import User
from services.image_service import ImageService
from core.config import settings
from core.database import get_db
from services.content_interceptor import content_interceptor


router = APIRouter(prefix="/api/v1/images", tags=["images"])

# 懒加载图片生成服务（避免启动时加载模型导致崩溃）
image_service = None

def get_image_service():
    """获取图片生成服务实例（懒加载）"""
    global image_service
    if image_service is None:
        image_service = ImageService()
    return image_service

# 确保上传目录存在
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ImageGenerateRequest(BaseModel):
    """图片生成请求"""
    prompt: str
    style: str = "luxury"
    platform: str = "amazon"


class BatchImageGenerateRequest(BaseModel):
    """批量图片生成请求"""
    products: list
    keyword: str
    add_overlay: bool = True


@router.post("/generate", summary="生成营销图片")
async def generate_image(
    request: ImageGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    生成营销图片

    Args:
        request: 图片生成请求（prompt + style）
        db: 数据库会话

    Returns:
        生成结果，包含图片 URL
    """
    try:
        # ====== Step 1: 输入审核（调用模型前） ======
        platform_lower = getattr(request, "platform", "amazon").lower()
        try:
            input_result = content_interceptor.intercept_text(
                db=db,
                platform=platform_lower,
                text_content=request.prompt,
            )
            if not input_result.passed:
                blocked_keywords = [v.matched_keyword for v in input_result.violations if v.severity == "block"]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "内容违规：检测到禁止使用的敏感词，无法生成相关内容",
                        "message": f"您输入的提示词中包含平台禁止的内容。命中敏感词：{', '.join(blocked_keywords)}。请修改后重试。",
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

        # ====== Step 2: 调用图片生成服务 ======
        # 调用图片生成服务（简化版，不需要用户认证）
        result = get_image_service().generate_marketing_image(
            product_name=request.prompt[:50],  # 截取前50字符作为产品名
            keyword=request.style,
            ref_image_path=None,
            add_overlay=False,
            db=db,
            user_id=None,
            profile_id=None
        )

        # ====== Step 3: 输出审核（OCR + 规则引擎） ======
        # 内容审核拦截 (OCR + 规则)
        try:
            image_path = result.get("image_path")
            if image_path:
                mod_result = content_interceptor.intercept_image(
                    db=db,
                    platform=platform_lower,
                    image_path=image_path,
                )
                if not mod_result.passed:
                    blocked_keywords = [v.matched_keyword for v in mod_result.violations if v.severity == "block"]
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "图片内容审核未通过",
                            "message": f"生成的图片中包含违规文字内容。命中敏感词：{', '.join(blocked_keywords)}。请尝试更换提示词后重新生成。",
                            "stage": "output_check",
                            "blocked_keywords": blocked_keywords,
                            "violations": [
                                {
                                    "category": v.category,
                                    "severity": v.severity,
                                    "matched_keyword": v.matched_keyword,
                                    "description": v.description,
                                }
                                for v in mod_result.violations
                                if v.severity == "block"
                            ]
                        }
                    )
        except HTTPException:
            raise
        except Exception as e:
            logging.getLogger(__name__).warning(f"Image moderation check failed (allowing through): {e}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片生成失败: {str(e)}"
        )


@router.post("/batch", summary="批量生成营销图片")
async def batch_generate_images(
    request: BatchImageGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    批量生成营销图片

    Args:
        request: 批量生成请求
        current_user: 当前登录用户

    Returns:
        批量生成结果列表
    """
    try:
        results = get_image_service().batch_generate_images(
            products=request.products,
            keyword=request.keyword,
            add_overlay=request.add_overlay
        )

        # 批量结果审核: 抽样检查每张图片的 OCR 文本
        try:
            db = next(get_db())
            for i, r in enumerate(results):
                image_path = r.get("image_path")
                if not image_path:
                    continue
                mod_result = content_interceptor.intercept_image(
                    db=db,
                    platform="amazon",
                    image_path=image_path,
                )
                if not mod_result.passed:
                    block_keywords = [
                        v.matched_keyword
                        for v in mod_result.violations
                        if v.severity == "block"
                    ]
                    r["moderation_status"] = "blocked"
                    r["blocked_keywords"] = block_keywords
                    logging.getLogger(__name__).warning(
                        f"Batch image[{i}] blocked: {block_keywords}"
                    )
                else:
                    r["moderation_status"] = "passed"
        except Exception as e:
            logging.getLogger(__name__).warning(f"Batch moderation check failed (allowing through): {e}")
        finally:
            db.close()

        return {
            "status": "success",
            "total": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量生成失败: {str(e)}"
        )

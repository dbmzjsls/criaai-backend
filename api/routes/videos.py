"""
视频生成 API 路由
使用 wan2.6-i2v 图生视频模型（无需登录验证）
"""
import logging
import os
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.video_service import video_service
from core.config import settings
from core.database import get_db
from services.content_interceptor import content_interceptor


router = APIRouter(prefix="/api/v1/videos", tags=["videos"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    prompt: str
    img_url: str
    duration: int = 5
    shot_type: str = 'single'
    resolution: str = '720P'
    profile_id: Optional[str] = None


@router.post("/generate", summary="生成视频（图生视频）")
async def generate_video(
    request: VideoGenerateRequest,
    db: Session = Depends(get_db),
):
    """使用 wan2.6-i2v 模型生成视频，无需登录"""
    try:
        # ====== Step 1: 输入审核（调用模型前） ======
        platform_lower = "amazon"
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

        # ====== Step 2: 调用视频生成 ======
        result = await video_service.generate_i2v(
            prompt=request.prompt,
            img_url=request.img_url,
            duration=request.duration,
            shot_type=request.shot_type,
            resolution=request.resolution,
            user_id=None,
            db=db,
            profile_id=None,
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"视频生成失败: {str(e)}")


@router.post("/upload-image", summary="上传图片用于视频生成")
async def upload_image(file: UploadFile = File(...)):
    """上传图片，返回图片路径供视频生成使用，无需登录"""
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持图片文件")

        ext = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        filename = f"upload_{uuid.uuid4().hex[:10]}{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)

        with open(filepath, 'wb') as f:
            content = await file.read()
            f.write(content)

        return {
            "status": "success",
            "img_url": f"/static/uploads/{filename}",
            "filename": filename
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"图片上传失败: {str(e)}")

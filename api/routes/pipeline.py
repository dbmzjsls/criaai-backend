"""
流水线路由模块
提供一条龙生成 API：文案→图片→视频
"""
import asyncio
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db
from services.pipeline_service import pipeline_service
from services.content_interceptor import content_interceptor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pipeline", tags=["流水线"])


class PipelineGenerateRequest(BaseModel):
    """一条龙生成请求"""
    keyword: str = Field(..., description="产品关键词", min_length=1)
    language: str = Field(default="zh", description="目标语言代码")
    style: str = Field(default="专业", description="文案风格")
    platform: str = Field(default="Amazon", description="目标平台")
    image_style: str = Field(default="luxury", description="图片风格")
    video_duration: int = Field(default=5, ge=5, le=10, description="视频时长(秒)")
    video_shot_type: str = Field(default="single", description="镜头类型")
    video_resolution: str = Field(default="720P", description="视频分辨率")


class PipelineGenerateResponse(BaseModel):
    """启动流水线响应"""
    task_id: str
    status: str


class PipelineTaskResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    current_step: str
    progress: dict
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/generate", response_model=PipelineGenerateResponse, status_code=status.HTTP_201_CREATED)
async def start_pipeline(
    request: PipelineGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    启动一条龙流水线：文案 → 图片 → 视频

    返回 task_id，前端轮询 GET /tasks/{task_id} 获取进度。
    步骤按顺序执行，每步完成后自动进入下一步。
    """
    task_id = str(uuid.uuid4())

    # ====== 输入审核 —— 调用流水线前检查关键词合规性 ======
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
        logger.warning(f"Pipeline input moderation check failed (allowing through): {e}")

    pipeline_service.store.create(task_id)

    # 使用 asyncio.create_task 确保任务在请求返回后继续执行
    params = request.model_dump()
    asyncio.create_task(
        asyncio.get_event_loop().run_in_executor(
            None, pipeline_service.run_pipeline_sync, db, params, task_id
        )
    )

    logger.info(f"Pipeline started: task_id={task_id}, keyword={request.keyword}")
    return PipelineGenerateResponse(task_id=task_id, status="pending")


@router.get("/tasks/{task_id}", response_model=PipelineTaskResponse)
async def get_task_status(task_id: str):
    """
    查询流水线任务进度

    轮询频率建议: 每 2-3 秒
    步骤: copywriting → image → video → done
    """
    task_dict = pipeline_service.store.to_dict(task_id)
    if task_dict is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在: {task_id}"
        )
    return PipelineTaskResponse(**task_dict)

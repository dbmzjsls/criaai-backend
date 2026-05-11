"""
流水线服务模块
编排文案→图片→视频一条龙生成流程
使用内存任务存储 + 轮询，适合 Railway 免费 MVP
"""
import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from services.copywriting_service import copywriting_service
from services.image_service import ImageService
from services.video_service import video_service
from core.monitoring import (
    record_pipeline_started, record_pipeline_completed, record_pipeline_failed,
    record_step_duration, record_ai_api_call,
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineTask:
    """流水线任务状态"""
    task_id: str
    status: str  # "pending" | "running" | "completed" | "failed"
    current_step: str  # "copywriting" | "image" | "video" | "done"
    progress: dict = field(default_factory=lambda: {
        "copywriting": "pending",
        "image": "pending",
        "video": "pending",
    })
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)


class PipelineTaskStore:
    """线程安全的内存任务存储"""

    def __init__(self):
        self._tasks: Dict[str, PipelineTask] = {}
        self._lock = threading.Lock()

    def create(self, task_id: str) -> PipelineTask:
        task = PipelineTask(task_id=task_id, status="pending", current_step="copywriting")
        with self._lock:
            self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Optional[PipelineTask]:
        with self._lock:
            return self._tasks.get(task_id)

    def update(self, task_id: str, **kwargs):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

    def update_progress(self, task_id: str, step: str, status: str):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.progress[step] = status
                task.current_step = step

    def set_result(self, task_id: str, result: dict):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.result = result
                task.status = "completed"
                task.current_step = "done"
                for step in task.progress:
                    task.progress[step] = "done"

    def set_error(self, task_id: str, error: str, failed_step: str):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "failed"
                task.error = error
                task.current_step = failed_step
                task.progress[failed_step] = "failed"

    def to_dict(self, task_id: str) -> Optional[dict]:
        task = self.get(task_id)
        if not task:
            return None
        return {
            "task_id": task.task_id,
            "status": task.status,
            "current_step": task.current_step,
            "progress": dict(task.progress),
            "result": task.result,
            "error": task.error,
        }


class PipelineService:
    """流水线编排服务"""

    def __init__(self):
        self.store = PipelineTaskStore()
        self._image_service: Optional[ImageService] = None

    def _get_image_service(self) -> ImageService:
        """懒加载 ImageService（避免启动时失败）"""
        if self._image_service is None:
            self._image_service = ImageService()
        return self._image_service

    def run_pipeline_sync(self, db: Session, params: dict, task_id: str):
        """
        同步执行流水线（运行在线程池中）

        步骤:
        1. 生成文案 (glm-5.1)
        2. 用文案生成图片 (wanx-v1)
        3. 用图片生成视频 (wan2.6-i2v)

        Args:
            db: 数据库会话
            params: 流水线参数
            task_id: 任务 ID
        """
        store = self.store
        store.update(task_id, status="running")
        record_pipeline_started()

        keyword = params.get("keyword", "")
        language = params.get("language", "zh")
        style = params.get("style", "专业")
        platform = params.get("platform", "Amazon")
        image_style = params.get("image_style", "luxury")
        video_duration = params.get("video_duration", 5)
        video_shot_type = params.get("video_shot_type", "single")
        video_resolution = params.get("video_resolution", "720P")

        # 语言代码映射
        lang_map = {
            "zh": "中文", "en": "英语", "pt": "葡语",
            "es": "西语", "fr": "法语", "de": "德语", "ja": "日语"
        }
        language_display = lang_map.get(language, language)

        # ====== Step 1: 文案生成 ======
        store.update_progress(task_id, "copywriting", "running")
        logger.info(f"[Pipeline {task_id}] Step 1: 开始生成文案...")
        t0 = time.time()

        try:
            copy_prompt = (
                f"你是一个专业的跨境电商营销文案专家。\n"
                f"为以下产品生成{language_display}营销文案，风格：{style}，平台：{platform}\n\n"
                f"产品关键词：{keyword}\n\n"
                f"请生成一段营销文案，要求：\n"
                f"1. 使用{language_display}语言\n"
                f"2. 突出产品特点和优势\n"
                f"3. 采用{style}风格\n"
                f"4. 适合{platform}平台的展示格式\n"
                f"5. 包含适当的关键词优化\n"
                f"6. 字数控制在200-300字之间\n\n"
                f"请直接输出文案内容，不需要额外的说明。"
            )
            t_call = time.time()
            copy_text = copywriting_service._call_dashscope_api(copy_prompt)
            record_ai_api_call(model="glm-5.1", duration=time.time() - t_call, success=True)
            record_step_duration(step="copywriting", duration=time.time() - t0)
            logger.info(f"[Pipeline {task_id}] 文案生成完成，{len(copy_text)} 字符")
        except Exception as e:
            record_ai_api_call(model="glm-5.1", duration=time.time() - t0, success=False)
            store.set_error(task_id, f"文案生成失败: {str(e)}", "copywriting")
            record_pipeline_failed()
            logger.error(f"[Pipeline {task_id}] 文案生成失败: {e}")
            return

        store.update_progress(task_id, "copywriting", "done")
        store.update(task_id, result={
            "copywriting": {"content": copy_text, "language": language, "product_name": keyword},
            "image": None,
            "video": None,
        })

        # ====== Step 2: 图片生成 ======
        store.update_progress(task_id, "image", "running")
        logger.info(f"[Pipeline {task_id}] Step 2: 开始生成图片...")
        t0 = time.time()

        try:
            img_svc = self._get_image_service()
            t_call = time.time()
            img_result = img_svc.generate_marketing_image(
                product_name=keyword,
                keyword=image_style,
                ref_image_path=None,
                add_overlay=False,
                db=None,
                user_id=None,
                profile_id=None,
            )
            record_ai_api_call(model="wanx-v1", duration=time.time() - t_call, success=True)
            record_step_duration(step="image", duration=time.time() - t0)
            image_path = img_result.get("image_path", "")
            image_url = img_result.get("image_url", "")
            logger.info(f"[Pipeline {task_id}] 图片生成完成: {image_url}")
        except Exception as e:
            record_ai_api_call(model="wanx-v1", duration=time.time() - t0, success=False)
            store.set_error(task_id, f"图片生成失败: {str(e)}", "image")
            record_pipeline_failed()
            logger.error(f"[Pipeline {task_id}] 图片生成失败: {e}")
            return

        store.update_progress(task_id, "image", "done")
        store.update(task_id, result={
            "copywriting": {"content": copy_text, "language": language, "product_name": keyword},
            "image": {"image_url": image_url, "image_path": image_path},
            "video": None,
        })

        # ====== Step 3: 视频生成 ======
        store.update_progress(task_id, "video", "running")
        logger.info(f"[Pipeline {task_id}] Step 3: 开始生成视频，使用图片: {image_path}")
        t0 = time.time()

        try:
            # 构建视频 prompt
            video_prompt = (
                f"Product showcase of {keyword}, "
                f"professional commercial style, smooth camera movement, "
                f"cinematic lighting, high quality product presentation"
            )

            # video_service.generate_i2v 是 async 方法，需要在新的事件循环中运行
            t_call = time.time()
            loop = asyncio.new_event_loop()
            try:
                video_result = loop.run_until_complete(
                    video_service.generate_i2v(
                        prompt=video_prompt,
                        img_url=image_path,
                        duration=video_duration,
                        shot_type=video_shot_type,
                        resolution=video_resolution,
                        user_id=None,
                        db=None,
                        profile_id=None,
                    )
                )
            finally:
                loop.close()
            record_ai_api_call(model="wan2.6-i2v", duration=time.time() - t_call, success=True)
            record_step_duration(step="video", duration=time.time() - t0)

            video_url = video_result.get("video_url", "")
            logger.info(f"[Pipeline {task_id}] 视频生成完成: {video_url}")
        except Exception as e:
            record_ai_api_call(model="wan2.6-i2v", duration=time.time() - t0, success=False)
            store.set_error(task_id, f"视频生成失败: {str(e)}", "video")
            record_pipeline_failed()
            logger.error(f"[Pipeline {task_id}] 视频生成失败: {e}")
            return

        # ====== 全部完成 ======
        record_pipeline_completed()
        store.set_result(task_id, {
            "copywriting": {"content": copy_text, "language": language, "product_name": keyword},
            "image": {"image_url": image_url, "image_path": image_path},
            "video": {"video_url": video_url, "duration": video_duration},
        })
        logger.info(f"[Pipeline {task_id}] 流水线全部完成!")


# 全局单例
pipeline_service = PipelineService()

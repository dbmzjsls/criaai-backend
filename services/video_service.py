"""
视频生成服务模块
使用 DashScope wan2.6-i2v 图生视频模型
参考官方 API: POST /api/v1/services/aigc/video-generation/video-synthesis
"""
import logging
import os
import uuid
import asyncio
import urllib.request
from http import HTTPStatus
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

import dashscope
from dashscope import VideoSynthesis

from core.config import settings
from services.asset_service import asset_service

logger = logging.getLogger(__name__)


class VideoService:
    """视频生成服务 - 基于 wan2.6-i2v 图生视频模型"""

    MODEL = 'wan2.6-i2v'

    def __init__(self):
        api_key = settings.DASHSCOPE_API_KEY
        if not api_key or not api_key.startswith('sk-'):
            raise ValueError("Invalid DASHSCOPE_API_KEY")
        dashscope.api_key = api_key

        self.output_dir = settings.OUTPUT_DIR
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.upload_dir, exist_ok=True)

    def _resolve_img_url(self, img_url: str) -> str:
        """
        将前端传来的相对路径转换为本地绝对路径（供 SDK 自动上传 OSS）
        CDN/HTTP URL 直接返回原值
        """
        if img_url.startswith('http://') or img_url.startswith('https://'):
            return img_url
        # /static/outputs/xxx.png → static/outputs/xxx.png
        local_path = img_url.lstrip('/')
        if os.path.exists(local_path):
            return os.path.abspath(local_path)
        raise ValueError(f"图片文件不存在: {img_url}")

    async def generate_i2v(
        self,
        prompt: str,
        img_url: str,
        duration: int = 5,
        shot_type: str = 'single',
        resolution: str = '720P',
        user_id: Optional[UUID] = None,
        db: Optional[Session] = None,
        profile_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        调用 wan2.6-i2v 生成视频

        官方 parameters 字段：
            resolution, prompt_extend, duration, shot_type, audio
        SDK 通过 **kwargs 映射到 parameters，prompt_extend 需用 extra_input 传递
        """
        resolved = self._resolve_img_url(img_url)
        logger.info(f"model={self.MODEL}, duration={duration}s, shot_type={shot_type}, resolution={resolution}")
        logger.info(f"img_url={resolved[:100]}")

        # VideoSynthesis.call() 是阻塞调用，放到线程池避免阻塞事件循环
        loop = asyncio.get_event_loop()
        try:
            rsp = await loop.run_in_executor(None, lambda: VideoSynthesis.call(
                model=self.MODEL,
                prompt=prompt,
                img_url=resolved,
                # 以下通过 **kwargs 映射到官方 API 的 parameters 字段
                duration=duration,
                shot_type=shot_type,
                resolution=resolution,
                prompt_extend=True,   # 官方字段名，直接通过 kwargs 传入
            ))
        except Exception as e:
            raise Exception(f"调用 DashScope API 失败: {type(e).__name__} - {e}")

        logger.info(f"status={rsp.status_code}, message={rsp.message}")

        if rsp.status_code != HTTPStatus.OK:
            raise Exception(f"视频生成失败 [{rsp.status_code}]: {rsp.message}")

        # 提取视频 URL
        try:
            video_cdn_url = rsp.output.video_url
            if not video_cdn_url or not video_cdn_url.startswith('http'):
                raise Exception("API 未返回有效的视频 URL")
        except (AttributeError, TypeError) as e:
            raise Exception(f"解析响应失败: {e}")

        logger.info(f"获取到视频 URL: {video_cdn_url[:100]}")

        # 下载视频到本地
        output_filename = f"video_{uuid.uuid4().hex[:10]}.mp4"
        output_path = os.path.join(self.output_dir, output_filename)
        try:
            urllib.request.urlretrieve(video_cdn_url, output_path)
        except Exception as e:
            raise Exception(f"下载视频失败: {e}")

        file_size = os.path.getsize(output_path)
        local_url = f"/static/outputs/{output_filename}"

        # 保存到资产库
        asset_id = None
        if db and user_id:
            try:
                asset = asset_service.save_asset(
                    db=db,
                    user_id=user_id,
                    asset_type="video",
                    content_data={
                        "video_url": local_url,
                        "prompt": prompt,
                        "source_img_url": img_url,
                        "duration": duration,
                        "shot_type": shot_type,
                    },
                    profile_id=profile_id,
                    asset_metadata={
                        "file_size": file_size,
                        "resolution": resolution,
                        "model": self.MODEL,
                        "generated_at": str(datetime.now()),
                    }
                )
                asset_id = str(asset.asset_id)
            except Exception as e:
                logger.warning(f"保存资产失败（不影响返回）: {e}")

        return {
            "status": "success",
            "video_url": local_url,
            "asset_id": asset_id,
            "duration": duration,
        }


video_service = VideoService()

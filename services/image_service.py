"""
图片生成服务模块
使用 Dashscope ImageSynthesis API 生成营销图片
"""
import logging
import os
import uuid
import urllib.request
from http import HTTPStatus
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
import dashscope
from dashscope import ImageSynthesis

from core.config import settings
from utils.image_processing import ImageProcessor
from services.asset_service import asset_service

logger = logging.getLogger(__name__)


class ImageService:
    """图片生成服务"""

    def __init__(self):
        """初始化图片生成服务"""
        # 设置 Dashscope API Key（确保使用 HTTPS 协议）
        api_key = settings.DASHSCOPE_API_KEY
        if not api_key or not api_key.startswith('sk-'):
            raise ValueError("Invalid DASHSCOPE_API_KEY: must start with 'sk-'")

        dashscope.api_key = api_key

        # 初始化图片处理器
        self.image_processor = ImageProcessor()

        # 确保输出目录存在
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_marketing_image(
        self,
        product_name: str,
        keyword: str,
        ref_image_path: Optional[str] = None,
        add_overlay: bool = True,
        db: Optional[Session] = None,
        user_id: Optional[UUID] = None,
        profile_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        生成营销图片

        Args:
            product_name: 产品名称
            keyword: 关键词/主题
            ref_image_path: 参考图片路径（可选）
            add_overlay: 是否添加文案叠加，默认为 True
            db: 数据库会话（可选，用于保存资产）
            user_id: 用户ID（可选，用于保存资产）
            profile_id: 产品档案ID（可选，用于关联产品）

        Returns:
            包含生成结果的字典，包括图片路径、URL、prompt 和 asset_id

        Raises:
            Exception: 图片生成失败时抛出异常
        """
        try:
            # 1. 构造 Prompt
            visual_prompt = (
                f"High-end commercial photography of {product_name}, professional studio lighting. "
                f"Visual theme: {keyword}. "
                "Minimalist composition, clean background with copy space on the bottom left, "
                "8k resolution, cinematic atmosphere, sharp focus."
            )

            logger.info(f"Generation params: product={product_name}, keyword={keyword}, ref_image={bool(ref_image_path)}")

            # 3. 调用通义万相 API（使用 SDK 默认配置，添加完整异常捕获）
            logger.info(f"正在调用通义万相 API, Prompt: {visual_prompt[:100]}..., Ref: {os.path.abspath(ref_image_path) if ref_image_path else 'None'}")

            try:
                # 调用 SDK，让其使用默认的 HTTPS 配置
                rsp = ImageSynthesis.call(
                    model=ImageSynthesis.Models.wanx_v1,
                    prompt=visual_prompt,
                    ref_img=os.path.abspath(ref_image_path) if ref_image_path else None,
                    n=1,
                    size='1024*1024'
                )

                logger.info(f"Response Status: {rsp.status_code}, Message: {rsp.message}")

            except ConnectionResetError as e:
                error_msg = f"网络连接被重置 (ConnectionResetError)，无法连接到阿里云服务器。请检查：1) API Key 是否有效 2) 网络连接是否正常 3) 防火墙是否拦截。详细错误: {str(e)}"
                logger.error(f"调用失败: {error_msg}")
                raise Exception(error_msg)
            except TimeoutError as e:
                error_msg = f"请求超时，阿里云服务器响应时间过长。详细错误: {str(e)}"
                logger.error(f"调用失败: {error_msg}")
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"调用阿里云 API 失败: {type(e).__name__} - {str(e)}"
                logger.error(f"调用失败: {error_msg}")
                raise Exception(error_msg)

            # 4. 验证响应状态
            if rsp.status_code != HTTPStatus.OK:
                error_msg = f"阿里云 API 返回错误状态: {rsp.status_code}, 消息: {rsp.message}"
                logger.error(f"调用失败: {error_msg}")
                raise Exception(error_msg)

            # 5. 验证返回的图片 URL
            try:
                img_cdn_url = rsp.output.results[0].url
                if not img_cdn_url or not img_cdn_url.startswith('http'):
                    raise Exception("API 返回的图片 URL 无效或为空")
                logger.info(f"获取到图片 URL: {img_cdn_url}")
            except (AttributeError, IndexError, TypeError) as e:
                error_msg = f"API 响应格式异常，无法提取图片 URL: {str(e)}"
                logger.error(f"调用失败: {error_msg}")
                raise Exception(error_msg)

            # 6. 下载图片
            output_filename = f"poster_{uuid.uuid4().hex[:10]}.png"
            final_save_path = os.path.join(self.output_dir, output_filename)

            try:
                urllib.request.urlretrieve(img_cdn_url, final_save_path)
                logger.info(f"图片已下载到: {final_save_path}")
            except Exception as e:
                error_msg = f"下载图片失败: {str(e)}"
                logger.error(f"调用失败: {error_msg}")
                raise Exception(error_msg)

            # 7. 添加文案叠加
            if add_overlay:
                try:
                    self.image_processor.add_commercial_overlay(final_save_path, product_name)
                except Exception as e:
                    logger.warning(f"添加文案叠加失败: {e}")

            # 8. 准备返回结果
            result = {
                "status": "success",
                "image_path": final_save_path,
                "image_url": f"/static/outputs/{output_filename}",
                "prompt": visual_prompt
            }

            # 9. 自动保存到资产库
            if db and user_id:
                try:
                    # 获取文件大小
                    file_size = os.path.getsize(final_save_path)

                    asset = asset_service.save_asset(
                        db=db,
                        user_id=user_id,
                        asset_type="image",
                        content_data={
                            "image_url": f"/static/outputs/{output_filename}",
                            "prompt": visual_prompt,
                            "product_name": product_name,
                            "keyword": keyword,
                            "has_overlay": add_overlay
                        },
                        profile_id=profile_id,
                        asset_metadata={
                            "file_size": file_size,
                            "dimensions": "1024x1024",
                            "generated_at": str(datetime.now()),
                            "ref_image_used": bool(ref_image_path)
                        }
                    )
                    result["asset_id"] = str(asset.asset_id)
                except Exception as e:
                    logger.warning(f"Failed to save asset: {e}")

            return result

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    def batch_generate_images(
        self,
        products: list,
        keyword: str,
        add_overlay: bool = True
    ) -> list:
        """
        批量生成营销图片

        Args:
            products: 产品列表，每个产品包含 name 字段
            keyword: 关键词/主题
            add_overlay: 是否添加文案叠加

        Returns:
            生成结果列表
        """
        results = []
        for product in products:
            try:
                result = self.generate_marketing_image(
                    product_name=product.get("name", "Product"),
                    keyword=keyword,
                    add_overlay=add_overlay
                )
                results.append({
                    "product": product,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "product": product,
                    "success": False,
                    "error": str(e)
                })

        return results

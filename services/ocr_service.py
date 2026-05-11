"""
Dashscope OCR 服务
从图片中提取文字，用于内容审核
"""
import base64
import http.client
import json
import logging
import os

from core.config import settings


class OCRService:
    """Dashscope OCR 文字识别服务"""

    MODEL = "qwen-vl-ocr-latest"

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY

    def extract_text(self, image_path: str) -> str:
        """
        从图片中提取文字

        Args:
            image_path: 图片文件路径

        Returns:
            识别出的文字（拼接后），失败返回空字符串
        """
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return ""

        # 读取并编码图片
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""

        # 判断图片 MIME 类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/png")

        conn = http.client.HTTPSConnection("dashscope.aliyuncs.com", timeout=30)
        try:
            payload = json.dumps({
                "model": self.MODEL,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"image": f"data:{mime_type};base64,{image_data}"},
                                {"text": "请识别并提取图片中的所有文字，直接输出文字内容，不要添加任何额外说明。"}
                            ]
                        }
                    ]
                }
            })
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            conn.request(
                "POST",
                "/api/v1/services/aigc/multimodal-generation/generation",
                payload, headers
            )
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))

            if res.status != 200:
                logging.getLogger(__name__).error(f"OCR API error (HTTP {res.status}): {data}")
                return ""

            # 提取响应中的文字
            output = data.get("output", {})
            choices = output.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                # content 可能是 list 或 string
                if isinstance(content, list):
                    texts = []
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            texts.append(item["text"])
                        elif isinstance(item, str):
                            texts.append(item)
                    return " ".join(texts)
                return str(content)

            return ""

        except Exception as e:
            logging.getLogger(__name__).error(f"OCR service error: {e}")
            return ""
        finally:
            conn.close()


# 全局单例
ocr_service = OCRService()

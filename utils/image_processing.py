"""
图片处理工具模块
提供图片叠加文案、样式处理等功能
"""
import logging
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional


class ImageProcessor:
    """图片处理器"""

    def __init__(self, font_path: Optional[str] = None):
        """
        初始化图片处理器

        Args:
            font_path: 字体文件路径，默认使用 Montserrat-Bold.ttf
        """
        if font_path is None:
            # 默认字体路径（相对于项目根目录）
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            font_path = os.path.join(base_dir, "Montserrat-Bold.ttf")

        self.font_path = font_path

    def add_commercial_overlay(
        self,
        image_path: str,
        product_name: str,
        promo_text: Optional[str] = None
    ) -> None:
        """
        为生成的底图叠加巴西风格的商业排版文字

        Args:
            image_path: 图片文件路径
            product_name: 产品名称
            promo_text: 促销文案，默认使用葡语促销语

        Raises:
            Exception: 图片处理失败时抛出异常
        """
        try:
            # 打开图片并转换为 RGBA 模式
            img = Image.open(image_path).convert("RGBA")
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)

            # 加载字体
            try:
                font_title = ImageFont.truetype(self.font_path, 58)
                font_slogan = ImageFont.truetype(self.font_path, 26)
            except Exception as e:
                logging.getLogger(__name__).warning(f"Font not found at {self.font_path}, using default font. Error: {e}")
                font_title = ImageFont.load_default()
                font_slogan = ImageFont.load_default()

            # 绘制巴西风格装饰块 (亮橙色)
            draw.rectangle([40, 720, 55, 860], fill=(255, 106, 0, 255))

            # 渲染传入的产品名称
            draw.text((80, 725), product_name.upper(), font=font_title, fill=(255, 255, 255, 255))

            # 自动添加葡语促销语
            if promo_text is None:
                promo_text = "QUALIDADE GARANTIDA | ENVIAMOS PARA TODO O BRASIL"
            draw.text((80, 810), promo_text, font=font_slogan, fill=(240, 240, 240, 200))

            # 合并图层并保存
            combined = Image.alpha_composite(img, txt_layer)
            combined.convert("RGB").save(image_path)

        except Exception as e:
            logging.getLogger(__name__).error(f"Text overlay failed: {e}")
            raise

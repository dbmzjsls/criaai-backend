"""
素材管理服务
处理素材上传、列表获取、删除等功能
"""
import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from models.asset import MediaLibrary
from models.user import User

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/mp3"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/mpeg", "video/quicktime"}

# 文件扩展名映射
EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/mp3": ".mp3",
    "video/mp4": ".mp4",
    "video/mpeg": ".mpeg",
    "video/quicktime": ".mov"
}

# 文件大小限制（字节）
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_AUDIO_SIZE = 20 * 1024 * 1024  # 20MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB


def validate_file_type(file: UploadFile) -> str:
    """验证文件类型并返回媒体类型"""
    content_type = file.content_type

    if content_type in ALLOWED_IMAGE_TYPES:
        return "image"
    elif content_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    elif content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {content_type}"
        )


def validate_file_size(file: UploadFile, media_type: str, file_size: int):
    """验证文件大小"""
    if media_type == "image" and file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"图片文件大小不能超过 {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    elif media_type == "audio" and file_size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"音频文件大小不能超过 {MAX_AUDIO_SIZE / 1024 / 1024}MB"
        )
    elif media_type == "video" and file_size > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"视频文件大小不能超过 {MAX_VIDEO_SIZE / 1024 / 1024}MB"
        )


async def upload_media(
    file: UploadFile,
    tags: Optional[List[str]],
    current_user: User,
    db: Session
) -> MediaLibrary:
    """上传素材文件"""
    # 验证文件类型
    media_type = validate_file_type(file)

    # 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)

    # 验证文件大小
    validate_file_size(file, media_type, file_size)

    # 生成唯一文件名
    file_extension = EXTENSION_MAP.get(file.content_type, ".bin")
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # 创建保存路径
    upload_dir = os.path.join("static", "uploads", media_type)
    os.makedirs(upload_dir, exist_ok=True)

    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 保存到数据库
    media = MediaLibrary(
        user_id=current_user.user_id,
        media_type=media_type,
        file_path=file_path,
        tags=tags
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    return media


def get_user_media(
    user_id: uuid.UUID,
    media_type: Optional[str],
    db: Session
) -> List[MediaLibrary]:
    """获取用户的素材列表"""
    query = db.query(MediaLibrary).filter(MediaLibrary.user_id == user_id)

    if media_type:
        query = query.filter(MediaLibrary.media_type == media_type)

    return query.order_by(MediaLibrary.uploaded_at.desc()).all()


def delete_media(
    media_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session
) -> bool:
    """删除素材"""
    media = db.query(MediaLibrary).filter(
        MediaLibrary.media_id == media_id,
        MediaLibrary.user_id == user_id
    ).first()

    if not media:
        raise HTTPException(status_code=404, detail="素材不存在")

    # 删除文件
    if os.path.exists(media.file_path):
        os.remove(media.file_path)

    # 从数据库删除
    db.delete(media)
    db.commit()

    return True

"""
素材库路由
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from core.database import get_db
from schemas.media import MediaUploadResponse, MediaListResponse, MediaDeleteResponse
from services.media_service import upload_media, get_user_media, delete_media

router = APIRouter(prefix="/api/v1/media", tags=["media"])

SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class _FakeUser:
    user_id = SYSTEM_USER_ID


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    media = await upload_media(file, tag_list, _FakeUser(), db)
    file_url = f"/static/uploads/{media.media_type}/{media.file_path.split('/')[-1]}"
    return MediaUploadResponse(
        media_id=media.media_id, user_id=media.user_id,
        media_type=media.media_type, file_path=media.file_path,
        file_url=file_url, tags=media.tags, uploaded_at=media.uploaded_at
    )


@router.get("", response_model=List[MediaListResponse])
async def get_media_list(
    media_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    media_list = get_user_media(SYSTEM_USER_ID, media_type, db)
    return [
        MediaListResponse(
            media_id=m.media_id, media_type=m.media_type,
            file_url=f"/static/uploads/{m.media_type}/{m.file_path.split('/')[-1]}",
            tags=m.tags, uploaded_at=m.uploaded_at
        )
        for m in media_list
    ]


@router.delete("/{media_id}", response_model=MediaDeleteResponse)
async def delete_media_file(media_id: UUID, db: Session = Depends(get_db)):
    success = delete_media(media_id, SYSTEM_USER_ID, db)
    return MediaDeleteResponse(success=success, message="素材删除成功")

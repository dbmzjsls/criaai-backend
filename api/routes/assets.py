"""
资产管理路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from core.database import get_db
from services.asset_service import asset_service

router = APIRouter(prefix="/api/v1/assets", tags=["资产管理"])

# 无登录模式：使用固定系统用户 UUID
SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class AssetResponse(BaseModel):
    asset_id: UUID
    user_id: UUID
    profile_id: Optional[UUID]
    asset_type: str
    content_data: dict
    asset_metadata: Optional[dict]
    version: int
    parent_asset_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    total: int
    assets: List[AssetResponse]


@router.get("", response_model=AssetListResponse)
async def get_assets(
    asset_type: Optional[str] = Query(None),
    profile_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    profile_uuid = UUID(profile_id) if profile_id else None
    assets = asset_service.get_user_assets(
        db=db, user_id=SYSTEM_USER_ID,
        asset_type=asset_type, profile_id=profile_uuid,
        skip=skip, limit=limit
    )
    return AssetListResponse(total=len(assets), assets=[AssetResponse.from_orm(a) for a in assets])


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    asset = asset_service.get_asset_by_id(db, asset_id, SYSTEM_USER_ID)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资产不存在")
    return AssetResponse.from_orm(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: UUID, db: Session = Depends(get_db)):
    try:
        asset_service.delete_asset(db, asset_id, SYSTEM_USER_ID)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{asset_id}/versions", response_model=List[AssetResponse])
async def get_asset_versions(asset_id: UUID, db: Session = Depends(get_db)):
    versions = asset_service.get_asset_versions(db, asset_id, SYSTEM_USER_ID)
    if not versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资产不存在")
    return [AssetResponse.from_orm(v) for v in versions]

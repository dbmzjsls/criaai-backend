from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from api.deps import get_db
from models.product import ProductProfile
from models.asset import ContentAsset, MediaLibrary

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    product_count = db.query(ProductProfile).count()
    asset_count = db.query(ContentAsset).count()
    today = datetime.now().date()
    today_count = db.query(ContentAsset).filter(
        func.date(ContentAsset.created_at) == today
    ).count()
    media_count = db.query(MediaLibrary).count()
    return {
        "productCount": product_count,
        "assetCount": asset_count,
        "todayCount": today_count,
        "mediaCount": media_count
    }


@router.get("/recent-assets")
async def get_recent_assets(limit: int = 5, db: Session = Depends(get_db)):
    assets = db.query(ContentAsset).order_by(
        ContentAsset.created_at.desc()
    ).limit(limit).all()
    return [
        {
            "id": str(asset.asset_id),
            "asset_type": asset.asset_type,
            "content_data": asset.content_data,
            "created_at": asset.created_at.isoformat()
        }
        for asset in assets
    ]


@router.get("/system-status")
async def get_system_status():
    return {"status": "operational", "version": "1.0.0", "uptime": "99.9%"}

"""
产品管理路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from schemas.product import ProductProfileCreate, ProductProfileUpdate, ProductProfileResponse
from services.product_service import (
    create_product, get_user_products, get_product_by_id, update_product, delete_product
)

router = APIRouter(prefix="/api/v1/products", tags=["产品管理"])

SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("", response_model=ProductProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_product_profile(product_data: ProductProfileCreate, db: Session = Depends(get_db)):
    return create_product(db, SYSTEM_USER_ID, product_data)


@router.get("", response_model=List[ProductProfileResponse])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_user_products(db, SYSTEM_USER_ID, skip, limit)


@router.get("/{product_id}", response_model=ProductProfileResponse)
async def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id, SYSTEM_USER_ID)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    return product


@router.put("/{product_id}", response_model=ProductProfileResponse)
async def update_product_profile(product_id: UUID, product_data: ProductProfileUpdate, db: Session = Depends(get_db)):
    product = update_product(db, product_id, SYSTEM_USER_ID, product_data)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_profile(product_id: UUID, db: Session = Depends(get_db)):
    success = delete_product(db, product_id, SYSTEM_USER_ID)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")

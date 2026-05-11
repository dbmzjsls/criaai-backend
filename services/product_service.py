"""
产品服务模块
处理产品档案的业务逻辑
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from models.product import ProductProfile
from schemas.product import ProductProfileCreate, ProductProfileUpdate


def create_product(
    db: Session,
    user_id: UUID,
    product_data: ProductProfileCreate
) -> ProductProfile:
    """
    创建产品档案

    Args:
        db: 数据库会话
        user_id: 用户 ID
        product_data: 产品创建数据

    Returns:
        创建的产品对象
    """
    new_product = ProductProfile(
        user_id=user_id,
        product_name=product_data.product_name,
        product_type=product_data.product_type,
        product_features=product_data.product_features,
        target_audience=product_data.target_audience,
        target_market=product_data.target_market,
        platform_channels=product_data.platform_channels
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def get_user_products(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[ProductProfile]:
    """
    获取用户的所有产品

    Args:
        db: 数据库会话
        user_id: 用户 ID
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        产品列表
    """
    return db.query(ProductProfile)\
        .filter(ProductProfile.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_product_by_id(
    db: Session,
    product_id: UUID,
    user_id: UUID
) -> Optional[ProductProfile]:
    """
    根据 ID 获取产品

    Args:
        db: 数据库会话
        product_id: 产品 ID
        user_id: 用户 ID（用于权限验证）

    Returns:
        产品对象，如果不存在或无权限返回 None
    """
    return db.query(ProductProfile)\
        .filter(
            ProductProfile.profile_id == product_id,
            ProductProfile.user_id == user_id
        )\
        .first()


def update_product(
    db: Session,
    product_id: UUID,
    user_id: UUID,
    product_data: ProductProfileUpdate
) -> Optional[ProductProfile]:
    """
    更新产品信息

    Args:
        db: 数据库会话
        product_id: 产品 ID
        user_id: 用户 ID（用于权限验证）
        product_data: 产品更新数据

    Returns:
        更新后的产品对象，如果不存在或无权限返回 None
    """
    product = get_product_by_id(db, product_id, user_id)
    if not product:
        return None

    # 更新字段
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(
    db: Session,
    product_id: UUID,
    user_id: UUID
) -> bool:
    """
    删除产品

    Args:
        db: 数据库会话
        product_id: 产品 ID
        user_id: 用户 ID（用于权限验证）

    Returns:
        删除成功返回 True，失败返回 False
    """
    product = get_product_by_id(db, product_id, user_id)
    if not product:
        return False

    db.delete(product)
    db.commit()

    return True

"""
资产管理服务模块
提供资产的保存、查询、删除和版本管理功能
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime
import os

from models.asset import ContentAsset
from models.product import ProductProfile


class AssetService:
    """资产管理服务"""

    def save_asset(
        self,
        db: Session,
        user_id: UUID,
        asset_type: str,
        content_data: Dict[str, Any],
        profile_id: Optional[UUID] = None,
        asset_metadata: Optional[Dict[str, Any]] = None
    ) -> ContentAsset:
        """
        保存资产到数据库

        Args:
            db: 数据库会话
            user_id: 用户ID
            asset_type: 资产类型 ('copywriting', 'image', 'video')
            content_data: 资产内容数据
            profile_id: 产品档案ID（可选）
            asset_metadata: 元数据（可选）

        Returns:
            创建的资产对象

        Raises:
            ValueError: 资产类型无效或数据验证失败
        """
        # 验证资产类型
        valid_types = ['copywriting', 'image', 'video']
        if asset_type not in valid_types:
            raise ValueError(f"无效的资产类型: {asset_type}")

        # 如果提供了 profile_id，验证产品是否存在且属于该用户
        if profile_id:
            product = db.query(ProductProfile).filter(
                and_(
                    ProductProfile.profile_id == profile_id,
                    ProductProfile.user_id == user_id
                )
            ).first()
            if not product:
                raise ValueError("产品不存在或无权访问")

        # 创建资产
        asset = ContentAsset(
            user_id=user_id,
            profile_id=profile_id,
            asset_type=asset_type,
            content_data=content_data,
            asset_metadata=asset_metadata or {},
            version=1
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    def get_user_assets(
        self,
        db: Session,
        user_id: UUID,
        asset_type: Optional[str] = None,
        profile_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ContentAsset]:
        """
        获取用户的资产列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            asset_type: 资产类型筛选（可选）
            profile_id: 产品档案ID筛选（可选）
            skip: 跳过记录数
            limit: 返回记录数限制

        Returns:
            资产列表
        """
        query = db.query(ContentAsset).filter(ContentAsset.user_id == user_id)

        # 应用筛选条件
        if asset_type:
            query = query.filter(ContentAsset.asset_type == asset_type)
        if profile_id:
            query = query.filter(ContentAsset.profile_id == profile_id)

        # 只返回主版本（非子版本）
        query = query.filter(ContentAsset.parent_asset_id.is_(None))

        # 按创建时间倒序排列
        query = query.order_by(ContentAsset.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def get_asset_by_id(
        self,
        db: Session,
        asset_id: UUID,
        user_id: UUID
    ) -> Optional[ContentAsset]:
        """
        根据ID获取资产

        Args:
            db: 数据库会话
            asset_id: 资产ID
            user_id: 用户ID（用于权限验证）

        Returns:
            资产对象，如果不存在或无权访问则返回 None
        """
        return db.query(ContentAsset).filter(
            and_(
                ContentAsset.asset_id == asset_id,
                ContentAsset.user_id == user_id
            )
        ).first()

    def delete_asset(
        self,
        db: Session,
        asset_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除资产

        Args:
            db: 数据库会话
            asset_id: 资产ID
            user_id: 用户ID（用于权限验证）

        Returns:
            是否删除成功

        Raises:
            ValueError: 资产不存在或无权访问
        """
        asset = self.get_asset_by_id(db, asset_id, user_id)
        if not asset:
            raise ValueError("资产不存在或无权访问")

        # 删除关联的文件（如果是图片或视频）
        if asset.asset_type in ['image', 'video']:
            file_path = asset.content_data.get('image_url') or asset.content_data.get('video_url')
            if file_path and file_path.startswith('/static/outputs/'):
                # 构建实际文件路径
                actual_path = file_path.replace('/static/outputs/', '')
                # 这里可以添加文件删除逻辑
                pass

        db.delete(asset)
        db.commit()
        return True

    def create_asset_version(
        self,
        db: Session,
        parent_asset_id: UUID,
        user_id: UUID,
        content_data: Dict[str, Any],
        asset_metadata: Optional[Dict[str, Any]] = None
    ) -> ContentAsset:
        """
        创建资产的新版本

        Args:
            db: 数据库会话
            parent_asset_id: 父资产ID
            user_id: 用户ID
            content_data: 新版本的内容数据
            asset_metadata: 元数据（可选）

        Returns:
            新版本资产对象

        Raises:
            ValueError: 父资产不存在或无权访问
        """
        # 获取父资产
        parent_asset = self.get_asset_by_id(db, parent_asset_id, user_id)
        if not parent_asset:
            raise ValueError("父资产不存在或无权访问")

        # 计算新版本号
        max_version = db.query(ContentAsset).filter(
            or_(
                ContentAsset.asset_id == parent_asset_id,
                ContentAsset.parent_asset_id == parent_asset_id
            )
        ).count()

        # 创建新版本
        new_version = ContentAsset(
            user_id=user_id,
            profile_id=parent_asset.profile_id,
            asset_type=parent_asset.asset_type,
            content_data=content_data,
            asset_metadata=asset_metadata or {},
            version=max_version + 1,
            parent_asset_id=parent_asset_id
        )

        db.add(new_version)
        db.commit()
        db.refresh(new_version)

        return new_version

    def get_asset_versions(
        self,
        db: Session,
        asset_id: UUID,
        user_id: UUID
    ) -> List[ContentAsset]:
        """
        获取资产的所有版本

        Args:
            db: 数据库会话
            asset_id: 资产ID
            user_id: 用户ID

        Returns:
            版本列表（按版本号排序）
        """
        # 验证资产存在且有权访问
        asset = self.get_asset_by_id(db, asset_id, user_id)
        if not asset:
            return []

        # 获取所有版本（包括主版本和子版本）
        versions = db.query(ContentAsset).filter(
            or_(
                ContentAsset.asset_id == asset_id,
                ContentAsset.parent_asset_id == asset_id
            )
        ).order_by(ContentAsset.version.asc()).all()

        return versions


# 全局服务实例
asset_service = AssetService()


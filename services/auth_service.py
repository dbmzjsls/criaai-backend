"""
认证服务模块
处理用户注册、登录、认证等业务逻辑
"""
from sqlalchemy.orm import Session
from typing import Optional

from models.user import User
from schemas.user import UserCreate
from core.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名查询用户

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        用户对象，如果不存在返回 None
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    根据邮箱查询用户

    Args:
        db: 数据库会话
        email: 邮箱地址

    Returns:
        用户对象，如果不存在返回 None
    """
    return db.query(User).filter(User.email == email).first()


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    注册新用户

    Args:
        db: 数据库会话
        user_data: 用户创建数据

    Returns:
        创建的用户对象

    Raises:
        ValueError: 用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    if get_user_by_username(db, user_data.username):
        raise ValueError("用户名已存在")

    # 检查邮箱是否已存在
    if get_user_by_email(db, user_data.email):
        raise ValueError("邮箱已被注册")

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        subscription_tier='free'
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    验证用户名和密码

    Args:
        db: 数据库会话
        username: 用户名
        password: 密码

    Returns:
        验证成功返回用户对象，失败返回 None
    """
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user

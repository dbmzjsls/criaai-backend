"""
认证路由模块
提供用户注册、登录、获取当前用户信息等 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import create_access_token
from core.config import settings
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from services.auth_service import register_user, authenticate_user
from api.deps import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册

    Args:
        user_data: 用户注册数据
        db: 数据库会话

    Returns:
        创建的用户信息

    Raises:
        HTTPException: 用户名或邮箱已存在时抛出 400 错误
    """
    try:
        user = register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录

    Args:
        login_data: 登录数据（用户名和密码）
        db: 数据库会话

    Returns:
        JWT Token

    Raises:
        HTTPException: 用户名或密码错误时抛出 401 错误
    """
    # 验证用户
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建 JWT Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息

    Args:
        current_user: 当前登录用户（从 JWT Token 中获取）

    Returns:
        当前用户信息
    """
    return current_user
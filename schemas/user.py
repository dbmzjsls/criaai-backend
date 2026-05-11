"""
用户 Pydantic 模型
用于 API 请求和响应的数据验证
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应模型"""
    user_id: UUID
    created_at: datetime
    subscription_tier: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据模型"""
    user_id: Optional[str] = None

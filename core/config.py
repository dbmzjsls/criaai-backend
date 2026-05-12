"""
配置管理模块
使用 pydantic-settings 从环境变量加载配置
"""
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """应用配置"""

    # 数据库: Railway 提供 DATABASE_URL，本地开发使用单独参数
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "1234"

    # JWT 配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时，适合生产环境

    # Dashscope API
    DASHSCOPE_API_KEY: str

    # 文件存储
    UPLOAD_DIR: str = "static/uploads"
    OUTPUT_DIR: str = "static/outputs"

    # CORS 允许的来源 (逗号分隔)
    CORS_ORIGINS: str = "http://localhost:3005,http://localhost:3000,http://localhost:5173"

    @property
    def database_url(self) -> str:
        """构建数据库连接 URL。优先使用 DATABASE_URL (Railway 自动注入)。"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_origin_list(self) -> List[str]:
        """解析 CORS origins 为列表"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()

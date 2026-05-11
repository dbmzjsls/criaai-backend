"""
千绘智能—电商内容共创平台 - 主应用入口
整合所有模块，提供完整的 API 服务
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ── 显式日志配置（修复 uvicorn 默认格式覆盖问题） ──────────────────
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "format": "%(asctime)s %(levelname)-5.5s [%(name)s] %(client_addr)s - \"%(request_line)s\" %(status_code)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn":        {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error":  {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"],  "level": "INFO", "propagate": False},
    },
}

# 导入路由
from api.routes import auth, products, copywriting, images, assets, videos, media, dashboard, search, moderation, pipeline

# 导入配置
from core.config import settings
from core.database import init_db, engine, get_db
from core.monitoring import setup_monitoring
from sqlalchemy import text

# 模块加载时立即应用日志配置（Procfile 和 python main_app.py 都生效）
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="千绘智能—电商内容共创平台",
    description="跨境电商 AI 内容生成平台",
    version="1.0.0"
)

# 配置 CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(copywriting.router)
app.include_router(images.router)
app.include_router(assets.router)
app.include_router(videos.router)
app.include_router(media.router)
app.include_router(search.router)
app.include_router(moderation.router)
app.include_router(pipeline.router)

# 启动时自动启用 pgvector 扩展（无需 Railway CLI）
@app.on_event("startup")
async def enable_pgvector():
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        logger.info("pgvector extension enabled (or already present)")
    except Exception as e:
        logger.warning(f"Could not enable pgvector extension: {e}")

# 安装 Prometheus 监控 (HTTP 中间件 + /metrics 端点)
setup_monitoring(app)

# 健康检查端点 - 验证数据库连接
@app.get("/health")
async def health_check():
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": "1.0.0"
    }

# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎使用千绘智能—电商内容共创平台",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("千绘智能—电商内容共创平台启动中...")
    logger.info(f"API 文档: /docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=LOGGING_CONFIG)

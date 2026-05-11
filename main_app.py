"""
千绘智能—电商内容共创平台 - 主应用入口
整合所有模块，提供完整的 API 服务
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 导入路由
from api.routes import auth, products, copywriting, images, assets, videos, media, dashboard, search, moderation, pipeline

# 导入配置
from core.config import settings
from core.database import init_db, get_db
from core.monitoring import setup_monitoring

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
    uvicorn.run(app, host="0.0.0.0", port=8000)

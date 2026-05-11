"""
Prometheus 监控模块
提供 /metrics 端点，用于 Grafana 仪表盘展示
"""
import time
import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

# ===== 应用信息 =====
app_info = Info("criaai_app", "CriaA.I. application info")
app_info.info({"version": "1.0.0", "python": "3.13", "framework": "fastapi"})

# ===== HTTP 指标 =====
http_requests_total = Counter(
    "criaai_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "criaai_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
)

http_requests_in_progress = Gauge(
    "criaai_http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method"],
)

# ===== Pipeline 指标 =====
pipeline_tasks_total = Counter(
    "criaai_pipeline_tasks_total",
    "Total pipeline tasks",
    ["status"],  # started, completed, failed
)

pipeline_tasks_in_progress = Gauge(
    "criaai_pipeline_tasks_in_progress",
    "Pipeline tasks currently running",
)

pipeline_step_duration_seconds = Histogram(
    "criaai_pipeline_step_duration_seconds",
    "Pipeline step duration",
    ["step"],  # copywriting, image, video
    buckets=[5.0, 10.0, 30.0, 60.0, 120.0, 180.0, 300.0, 600.0],
)

# ===== AI API 调用指标 =====
ai_api_requests_total = Counter(
    "criaai_ai_api_requests_total",
    "Total AI API calls",
    ["provider", "model", "status"],  # provider=dashscope, model=qwen-plus/wanx-v1/wan2.6-i2v
)

ai_api_request_duration_seconds = Histogram(
    "criaai_ai_api_request_duration_seconds",
    "AI API call duration in seconds",
    ["provider", "model"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 180.0, 300.0, 600.0],
)

# ===== 数据库指标 =====
db_connections_active = Gauge(
    "criaai_db_connections_active",
    "Active database connections",
)


class PrometheusMiddleware:
    """FastAPI Prometheus 中间件 — 记录 HTTP 请求指标"""

    def __init__(self, app: FastAPI):
        @app.middleware("http")
        async def prometheus_middleware(request: Request, call_next: Callable):
            method = request.method
            path = request.url.path

            # 跳过 /metrics 自身避免无限循环
            if path == "/metrics":
                return await call_next(request)

            # 路由模式化（/api/v1/pipeline/tasks/{uuid} → /api/v1/pipeline/tasks/{task_id}）
            route = _get_route_pattern(request)

            http_requests_in_progress.labels(method=method).inc()
            start = time.time()
            try:
                response = await call_next(request)
                status = str(response.status_code)
            except Exception:
                status = "500"
                raise
            finally:
                duration = time.time() - start
                http_requests_in_progress.labels(method=method).dec()
                http_requests_total.labels(method=method, endpoint=route, status=status).inc()
                http_request_duration_seconds.labels(method=method, endpoint=route).observe(duration)

            return response


def _get_route_pattern(request: Request) -> str:
    """将具体路径转为路由模式"""
    path = request.url.path
    # /api/v1/pipeline/tasks/<uuid> → /api/v1/pipeline/tasks/{task_id}
    parts = path.split("/")
    for i, part in enumerate(parts):
        # UUID pattern
        if len(part) in (32, 36) and "-" in part:
            parts[i] = "{id}"
        # hex id pattern
        elif len(part) >= 8 and all(c in "0123456789abcdef" for c in part):
            parts[i] = "{id}"
    return "/".join(parts)


def setup_monitoring(app: FastAPI):
    """
    配置 FastAPI 应用的 Prometheus 监控

    将 /metrics 端点注册到应用，并安装 HTTP 中间件
    """
    # 注册 /metrics 端点
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # 安装中间件
    PrometheusMiddleware(app)

    logger.info("Prometheus monitoring enabled — /metrics endpoint registered")


# ===== Pipeline 工具函数 =====

def record_pipeline_started():
    pipeline_tasks_total.labels(status="started").inc()
    pipeline_tasks_in_progress.inc()


def record_pipeline_completed():
    pipeline_tasks_total.labels(status="completed").inc()
    pipeline_tasks_in_progress.dec()


def record_pipeline_failed():
    pipeline_tasks_total.labels(status="failed").inc()
    pipeline_tasks_in_progress.dec()


def record_step_duration(step: str, duration: float):
    pipeline_step_duration_seconds.labels(step=step).observe(duration)


def record_ai_api_call(model: str, duration: float, success: bool):
    status = "success" if success else "error"
    ai_api_requests_total.labels(provider="dashscope", model=model, status=status).inc()
    ai_api_request_duration_seconds.labels(provider="dashscope", model=model).observe(duration)

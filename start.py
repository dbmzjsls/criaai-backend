"""
CriaAI 启动脚本 — 核武级日志控制
深拷贝 Uvicorn 内置 LOGGING_CONFIG + 启动前清空所有残留 handler
"""
import copy
import logging
import os
import sys
import uvicorn
from uvicorn.config import LOGGING_CONFIG

# ── 核武级清空：杀死所有已存在的 logger handler ──────────────────
for name in logging.root.manager.loggerDict:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.propagate = True

root = logging.getLogger()
for h in list(root.handlers):
    root.removeHandler(h)

# ── 深拷贝 Uvicorn 默认配置 ────────────────────────────────────────
log_config = copy.deepcopy(LOGGING_CONFIG)

# ── 强制接管根日志 + 关闭已存在的 logger ──────────────────────────
log_config["disable_existing_loggers"] = True
log_config["loggers"][""] = {"handlers": ["default"], "level": "INFO"}

# ── 开启颜色 ──────────────────────────────────────────────────────
log_config["use_colors"] = True
log_config["formatters"]["default"]["use_colors"] = True
log_config["formatters"]["access"]["use_colors"] = True

# ── 自定义格式：时间 + 等级 + 模块 + 消息 ──────────────────────────
log_config["formatters"]["default"]["fmt"] = (
    "%(asctime)s | %(levelprefix)s [%(name)s] %(message)s"
)
log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

log_config["formatters"]["access"]["fmt"] = (
    "%(asctime)s | %(levelprefix)s | "
    '%(client_addr)s — "%(request_line)s" %(status_code)s'
)
log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

# ── 确保流输出 ──────────────────────────────────────────────────────
log_config["handlers"]["default"]["stream"] = "ext://sys.stderr"
log_config["handlers"]["access"]["stream"] = "ext://sys.stdout"

# ── 启动 ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(
        "main_app:app",
        host="0.0.0.0",
        port=port,
        log_config=log_config,
    )

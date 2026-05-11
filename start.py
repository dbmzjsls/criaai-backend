"""
CriaAI 启动脚本 - 内联日志配置，避免外部文件路径问题
"""
import logging
import os
import uvicorn

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "logging.Formatter",
            "format": "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "logging.Formatter",
            "format": '%(asctime)s %(levelname)-5.5s [%(name)s] %(client_addr)s - "%(request_line)s" %(status_code)s',
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
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

if __name__ == "__main__":
    uvicorn.run(
        "main_app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_config=LOG_CONFIG,
    )

"""
CriaAI 启动脚本
深拷贝 Uvicorn 内置 LOGGING_CONFIG，仅替换日志格式，
完整保留原生的颜色显示、处理器流、Logger 层级等所有默认行为。

核心逻辑：
  - 不传裸 dict（会被 Uvicorn 内部覆盖回默认格式）
  - 从 uvicorn.config 导入默认 LOGGING_CONFIG 并 copy.deepcopy
  - 只改 formatters 里的 fmt / datefmt，其余全部不动
"""
import copy
import os
import uvicorn
from uvicorn.config import LOGGING_CONFIG

# ── 深拷贝默认日志配置 ──────────────────────────────────────────────
log_config = copy.deepcopy(LOGGING_CONFIG)

# ── 强制关闭已存在的 logger，防止 basicConfig() 等"幽灵"格式残留 ──
log_config["disable_existing_loggers"] = True

# ── 保留 Uvicorn 原生颜色 ──────────────────────────────────────────
log_config["use_colors"] = True
log_config["formatters"]["default"]["use_colors"] = True
log_config["formatters"]["access"]["use_colors"] = True

# ── 自定义 Default Formatter ──────────────────────────────────────
# 使用 %(levelprefix)s 而非 %(levelname)s，以保留 Uvicorn 彩色等级标签
log_config["formatters"]["default"]["fmt"] = (
    "%(asctime)s %(levelprefix)s [%(name)s] %(message)s"
)
log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

# ── 自定义 Access Formatter ───────────────────────────────────────
# 时间 + 彩色等级 + 客户端IP + 请求方法/路径 + 状态码
log_config["formatters"]["access"]["fmt"] = (
    '%(asctime)s %(levelprefix)s %(client_addr)s - '
    '"%(request_line)s" %(status_code)s'
)
log_config["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"

# ── 确保流输出到标准位置 ──────────────────────────────────────────
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

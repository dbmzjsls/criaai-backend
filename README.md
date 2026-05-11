# 千绘智能 · CriaA.I.

> 拉美电商 AI 内容共创平台 — 文案、图片、视频，一条龙生成

---

## 功能

| 模块 | 说明 |
|------|------|
| **AI 文案** | 多语言营销文案（中文 / English / Português / Español），6 种文案类型，4 种语气风格 |
| **AI 图片** | 产品图、海报、广告创意，6 种风格，4 种比例，4 种光照，4 种构图 |
| **AI 视频** | wan2.6-i2v 图生视频，5-10 秒，720P/1080P，支持本地上传或 URL 参考图 |
| **一条龙流水线** | 输入关键词 → 自动完成 文案 → 图片 → 视频，实时轮询进度 |
| **素材库** | 统一管理生成结果 |
| **产品管理** | 管理产品档案，用于 AI 内容生成 |

---

## 技术栈

### 后端
- **FastAPI** + SQLAlchemy + pgvector
- **DashScope** (通义千问 / 万相) — AI 模型
- **PostgreSQL** — 数据库 + 向量存储
- **Prometheus + Grafana** — 监控

### 前端
- **React 18** + Vite 5
- **Tailwind CSS** — Cyberpunk / Neon 风格
- **Three.js** — 3D 可视化
- **Framer Motion** — 动画

---

## 快速开始

### 环境要求
- Python ≥ 3.13
- Node.js ≥ 18
- PostgreSQL + pgvector
- uv 包管理器

### 后端

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DATABASE_URL、SECRET_KEY、DASHSCOPE_API_KEY

# 数据库迁移
uv run alembic upgrade head

# 启动
uv run uvicorn main_app:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:3005

---

## 部署

详见 [部署指南](./CriaAI-部署指南.md)

- **后端**: Railway (免费计划)
- **前端**: Vercel (Hobby 计划)
- **数据库**: Railway PostgreSQL + pgvector

---

## 项目结构

```
criaai-backend/
├── main_app.py              # FastAPI 入口
├── Procfile                 # Railway 启动命令
├── Dockerfile               # Docker 构建
├── pyproject.toml           # Python 依赖
│
├── api/routes/              # API 路由
│   ├── pipeline.py          # 一条龙流水线
│   ├── copywriting.py       # 文案生成
│   ├── images.py            # 图片生成
│   ├── videos.py            # 视频生成
│   └── ...
│
├── services/                # 业务逻辑
├── models/                  # 数据库模型
├── core/                    # 核心配置
│
├── frontend/                # React 前端
│   └── src/pages/
│       ├── PipelinePage.jsx # 一条龙 Wizard UI
│       ├── DashboardPage.jsx
│       └── ...
│
├── grafana/                 # Grafana 预置仪表盘
└── static/                  # 文件存储
```

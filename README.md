# 千绘智能 · CriaAI

> 电子商务 AI 内容共创平台 — 文案、图片、视频，一条龙生成
> **核心驱动：RAG（检索增强生成）+ 向量语义检索**

---

## 核心亮点：RAG 增强检索

平台通过**检索增强生成（Retrieval-Augmented Generation）**架构，将向量语义检索与 LLM 生成深度融合，确保 AI 产出精准匹配品类特征和用户意图。

```
用户输入关键词
      │
      ▼
┌─────────────────┐
│  内容审核拦截器   │  ← 输入合规检查（敏感词过滤）
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  向量语义检索     │  ← DashScope text-embedding-v4 (1024维)
│  pgvector 余弦搜索 │  ← PostgreSQL + pgvector 扩展
│  Top-K 相似产品   │  ← 自动品类聚合分析
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RAG 上下文构建   │  ← 品类分布统计 + 相似度过滤 (cos < 0.8)
│  增强提示词注入   │  ← 将检索结果注入 LLM System Prompt
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM 生成        │  ← 通义千问 (Qwen3.5-Flash) 生成文案
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  输出审核         │  ← 输出合规检查后返回
└─────────────────┘
```

### RAG 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **嵌入模型** | DashScope `text-embedding-v4` | 1024 维文本嵌入，支持批量处理 + 指数退避重试 |
| **向量存储** | PostgreSQL + pgvector | 余弦距离 (`<->`) 语义搜索，SQLAlchemy ORM 封装 |
| **检索策略** | 语义相似度 Top-K + 品类过滤 | 自动分析品类分布，过滤低相似度结果 |
| **上下文注入** | 结构化 Prompt 增强 | 将检索结果（品类、数量、风格）注入 System Prompt |
| **安全护栏** | 双层内容审核 | 输入审核（生成前）+ 输出审核（生成后）|

---

## 功能

| 模块 | 说明 |
|------|------|
| **RAG 文案生成** | 向量检索增强的多语言营销文案（中文 / English / Português / Español），6 种文案类型，4 种语气风格 |
| **向量语义搜索** | 基于嵌入的产品语义搜索、相似产品推荐、向量库统计 |
| **AI 图片** | 产品图、海报、广告创意，6 种风格，4 种比例，4 种光照，4 种构图 |
| **AI 视频** | wan2.6-i2v 图生视频，5-10 秒，720P/1080P，支持本地上传或 URL 参考图 |
| **一条龙流水线** | 输入关键词 → 自动完成 文案 → 图片 → 视频，实时轮询进度 |
| **素材库** | 统一管理生成结果 |
| **产品管理** | 管理产品档案，用于 AI 内容生成 |

---

## 技术栈

### 后端
- **FastAPI** + SQLAlchemy + pgvector
- **DashScope** (通义千问 Qwen3.5-Flash / 万相 wan2.6-i2v) — AI 模型
- **DashScope text-embedding-v4** — 文本嵌入（RAG 核心）
- **PostgreSQL + pgvector** — 数据库 + 向量存储 + 余弦相似度搜索
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

# 启动（pgvector 扩展自动启用）
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

## API 概览

### RAG / 向量搜索

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/search/products` | 语义产品搜索 (query → embedding → pgvector) |
| `GET` | `/api/v1/search/products/{id}/similar` | 基于嵌入相似度的产品推荐 |
| `GET` | `/api/v1/search/stats` | 向量库统计（嵌入总数）|
| `POST` | `/api/v1/copywriting/generate` | **RAG 增强文案生成**（检索 → 注入 → 生成 → 审核）|

### 流水线 / 素材

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/pipeline/generate` | 启动全流程（文案+图片+视频）|
| `GET` | `/api/v1/pipeline/tasks/{task_id}` | 轮询任务状态 |
| `GET` | `/api/v1/dashboard/stats` | 全局统计 |

---

## 部署

详见 [部署指南](./CriaAI-部署指南.md)

- **后端**: Railway + Dockerfile (自定义日志格式)
- **前端**: Vercel (Hobby 计划)
- **数据库**: Railway PostgreSQL + pgvector

---

## 项目结构

```
criaai-backend/
├── main_app.py              # FastAPI 入口
├── start.py                 # 生产启动脚本（自定义日志格式）
├── Procfile                 # Railway 进程定义
├── Dockerfile               # Docker 构建
├── pyproject.toml           # Python 依赖
│
├── services/
│   ├── vector_service.py    # ★ RAG 核心：向量检索 + 上下文构建
│   ├── copywriting_service.py   # LLM 调用（RAG 增强 Prompt）
│   ├── pipeline_service.py      # 一条龙流水线
│   └── content_interceptor.py   # 内容审核
│
├── utils/
│   └── embeddings.py        # ★ 嵌入服务：text-embedding-v4 批量嵌入
│
├── models/
│   └── embedding.py         # ★ pgvector 向量存储模型（Vector(1024)）
│
├── api/routes/
│   ├── search.py            # ★ 语义搜索 API
│   ├── copywriting.py       # ★ RAG 增强文案生成 API
│   ├── pipeline.py          # 一条龙流水线 API
│   ├── images.py            # 图片生成 API
│   ├── videos.py            # 视频生成 API
│   └── ...
│
├── core/                    # 核心配置、数据库、监控
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

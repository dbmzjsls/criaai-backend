FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for psycopg2 (libpq-dev + gcc) and Pillow (libjpeg, zlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies (production only)
RUN uv sync --frozen --no-dev

# Copy application code (excluding .env via .dockerignore)
COPY . .

# Run database migrations then start server
CMD uv run alembic upgrade head && uv run uvicorn main_app:app --host 0.0.0.0 --port ${PORT:-8000}

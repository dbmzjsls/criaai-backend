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

# Purge stale __pycache__ to ensure no old .pyc bytecode survives
RUN find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
RUN find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Run database migrations, seed moderation rules & product embeddings, then start server
CMD uv run alembic upgrade head && uv run python scripts/seed_moderation_rules.py --reset && uv run python scripts/seed_embeddings.py && uv run python start.py

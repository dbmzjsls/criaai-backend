web: cat log_config.json && uv run alembic upgrade head && uv run python -c "import uvicorn; uvicorn.run('main_app:app', host='0.0.0.0', port=int('${PORT:-8000}'), log_config='log_config.json')"

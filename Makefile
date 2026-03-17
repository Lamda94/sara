.PHONY: dev test lint db migrate models

# Desarrollo
dev:
	uvicorn sara.main:app --reload --host 0.0.0.0 --port 8000

# Base de datos
db:
	docker compose up -d db

# Migraciones
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(MSG)"

# Modelos ML
models:
	python scripts/download_models.py

# Tests
test:
	pytest -v

# Lint
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

# Docker
up:
	docker compose up -d

down:
	docker compose down

# Instalar dependencias
install:
	uv pip install -e ".[dev]"

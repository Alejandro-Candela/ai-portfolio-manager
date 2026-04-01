.PHONY: dev backend frontend db migrate test lint format install clean

# ── Development ──

dev: ## Start all services (postgres + backend + frontend)
	@echo "Starting all services..."
	$(MAKE) db &
	sleep 3
	$(MAKE) backend &
	$(MAKE) frontend

backend: ## Start FastAPI backend
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Start Next.js frontend
	cd frontend && bun dev

db: ## Start PostgreSQL via Docker
	docker compose up postgres

db-reset: ## Reset database (destroy + recreate)
	docker compose down -v postgres
	docker compose up -d postgres

# ── Database Migrations ──

migrate: ## Run Alembic migrations
	uv run alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	uv run alembic revision --autogenerate -m "$(MSG)"

# ── Quality ──

test: ## Run tests
	uv run pytest -v

test-cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=html -v

lint: ## Run linter
	uv run ruff check src/ tests/
	uv run mypy src/

format: ## Format code
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

# ── Setup ──

install: ## Install all dependencies
	uv sync --all-extras
	cd frontend && bun install

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true

# ── Docker ──

docker-up: ## Start all services via Docker Compose
	docker compose up --build

docker-down: ## Stop all Docker services
	docker compose down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

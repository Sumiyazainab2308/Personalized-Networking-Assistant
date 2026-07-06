# ─────────────────────────────────────────────────────────────────────────────
# Personalized Networking Assistant — Makefile
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install dev-backend dev-frontend test test-cov lint format \
        docker-build docker-up docker-down docker-logs clean

PYTHON     := python
VENV       := venv
PIP        := $(VENV)/Scripts/pip
PYTEST     := $(VENV)/Scripts/pytest
UVICORN    := $(VENV)/Scripts/uvicorn
STREAMLIT  := $(VENV)/Scripts/streamlit

# Default target
help:  ## Show this help message
	@echo ""
	@echo "  Personalized Networking Assistant — Makefile"
	@echo "  ─────────────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────
install: ## Create venv and install all dependencies
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "  ✅ Installation complete. Run 'make dev-backend' to start the API."

# ── Development servers ───────────────────────────────────────────────────────
dev-backend: ## Start FastAPI backend with hot-reload
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## Start Streamlit frontend
	$(STREAMLIT) run frontend/streamlit_app.py \
		--server.port 8501 \
		--server.address 0.0.0.0

dev: ## Start both servers (in background — open two terminals for interactive)
	@echo "Start backend:  make dev-backend"
	@echo "Start frontend: make dev-frontend"

# ── Testing ───────────────────────────────────────────────────────────────────
test: ## Run all tests
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage report
	$(PYTEST) tests/ -v \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-fail-under=80

test-fast: ## Run tests without slow NLP tests
	$(PYTEST) tests/ -v -m "not slow"

# ── Code Quality ──────────────────────────────────────────────────────────────
lint: ## Run ruff linter
	$(VENV)/Scripts/ruff check app/ tests/ frontend/

format: ## Auto-format code with ruff
	$(VENV)/Scripts/ruff format app/ tests/ frontend/

# ── Docker ────────────────────────────────────────────────────────────────────
docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start services with Docker Compose
	docker compose up -d

docker-down: ## Stop Docker Compose services
	docker compose down

docker-logs: ## Stream Docker logs
	docker compose logs -f

docker-restart: ## Restart all Docker services
	docker compose restart

# ── Utilities ─────────────────────────────────────────────────────────────────
clean: ## Remove build artifacts, caches, and temp files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleaned build artifacts."

data-reset: ## Clear the local history JSON (CAUTION: irreversible)
	@echo '[]' > data/history.json
	@echo '[]' > data/profiles.json
	@echo "✅ History and profiles cleared."

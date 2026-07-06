# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2024-07-03

### 🎉 Initial Release

#### Added

**Backend (FastAPI)**
- `POST /api/v1/analyze-event` — DistilBERT/BART zero-shot event classification
- `POST /api/v1/generate-conversation` — GPT-2 powered conversation starter generation
- `GET /api/v1/fact-check` — Wikipedia API fact verification with multi-query support
- `GET /api/v1/history` — Paginated session history with search filtering
- `GET /api/v1/history/analytics` — Aggregate analytics (theme counts, avg ratings, sessions/day)
- `GET /api/v1/history/export/json` — Full history export as JSON download
- `GET /api/v1/history/export/csv` — Full history export as CSV download
- `POST /api/v1/feedback` — Star rating (1–5) and text comment feedback submission
- `GET /health` — Application health and model load status
- Lazy model loading with thread-safe singleton pattern
- Custom exception hierarchy with structured JSON error responses
- Request logging middleware (method, path, status, timing)
- CORS middleware for Streamlit frontend integration
- Pydantic v2 request/response models with field validators
- Local JSON persistence with atomic file writes
- SOLID architecture: separate services for NLP, generation, fact-check, storage
- Full type hints and Google-style docstrings throughout

**Frontend (Streamlit)**
- Premium dark-themed UI with gradient hero header and custom CSS
- Sidebar: professional bio input, num_starters slider, API health status
- Main page: event description input, analyze/generate actions
- Theme analysis with bar chart visualization and badge display
- Conversation starters as styled cards with copy/download functionality
- Inline star rating feedback panel
- Fact-check panel pre-populated with detected event themes
- Recent sessions history panel with expandable details
- Dashboard page: metrics, theme bar chart, sessions time series, recent table
- History browser: pagination, keyword search, session detail view
- Export buttons for JSON and CSV downloads

**Infrastructure**
- Multi-stage Dockerfile with non-root user
- Docker Compose with health checks, volume mounts, shared network
- `Makefile` with targets: install, dev-backend, dev-frontend, test, test-cov, docker-*
- `requirements.txt` with pinned minimum versions
- `.env.example` template for all environment variables
- MIT License
- `CONTRIBUTING.md` with workflow, standards, and commit conventions

**Testing**
- `pytest` + `pytest-asyncio` test suite
- Mocked Hugging Face and Wikipedia calls
- Tests for: analyze, generate, fact-check, history, feedback endpoints
- Coverage for success paths, validation, edge cases, and persistence
- `conftest.py` with isolated temp-dir settings and shared fixtures

---

## [Unreleased]

### Planned
- User authentication and multi-user support
- Semantic search over history (vector embeddings)
- GPT-4 / Claude integration for higher-quality starters
- Email/Slack notification for scheduled events
- Mobile-responsive PWA frontend
- PostgreSQL backend option for production deployments

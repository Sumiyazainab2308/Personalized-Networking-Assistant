# Personalized Networking Assistant — Implementation Plan

## Overview

A full-stack AI-powered networking assistant that analyzes events, generates conversation starters, performs fact-checking via Wikipedia, and tracks session history — built with FastAPI + Streamlit + Hugging Face Transformers following SOLID architecture principles.

## Architecture (from diagram)

```
User Interface (Streamlit)
  ├── User Input Area (Bio & Event Desc.)
  ├── Generation Engine Control (Generate / Fact-Check)
  └── Output Display (Starters + Fact Status)
           │ HTTPS/JSON
FastAPI Backend
  ├── API Endpoints: POST /analyze-event, POST /generate-conversation,
  │                  GET /fact-check, GET /history, POST /feedback
  └── Orchestration & Request Handler
           │
AI & NLP Services (Local Transformers)
  ├── DistilBERT Zero-Shot Classification (Event Theme Analysis)
  ├── GPT-2 Small Text Generation (Starter Text Generation)
  └── Context Query Formulation
           │
Fact Verification Module ←→ Wikipedia Search & Lookup API
           │
Local Data Store (JSON)
  ├── User Profiles (Bio data)
  └── Interaction Logs (for auditing)
```

## Project Structure

```
networking-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Settings & env vars
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py            # Pydantic request models
│   │   └── responses.py           # Pydantic response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── analyze.py             # POST /analyze-event
│   │   ├── generate.py            # POST /generate-conversation
│   │   ├── factcheck.py           # GET /fact-check
│   │   ├── history.py             # GET /history
│   │   └── feedback.py            # POST /feedback
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py         # DistilBERT zero-shot
│   │   ├── generation_service.py  # GPT-2 generation
│   │   ├── factcheck_service.py   # Wikipedia API
│   │   ├── storage_service.py     # JSON persistence
│   │   └── orchestrator.py        # Orchestration logic
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Logging setup
│       └── exceptions.py          # Custom exceptions
├── frontend/
│   ├── streamlit_app.py           # Main Streamlit app
│   ├── pages/
│   │   ├── dashboard.py           # Analytics dashboard
│   │   └── history.py             # History browser
│   └── components/
│       ├── sidebar.py             # Sidebar config
│       └── cards.py               # UI card components
├── data/
│   ├── history.json               # Interaction logs
│   └── profiles.json              # User profiles
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_analyze.py
│   ├── test_generate.py
│   ├── test_factcheck.py
│   ├── test_history.py
│   └── test_feedback.py
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── Makefile
├── README.md
└── requirements.txt
```

## Proposed Changes

### Backend (FastAPI)
- SOLID: each router handles one endpoint group, each service handles one concern
- Lazy model loading via `@lru_cache` / singleton pattern
- Full type hints, docstrings, logging
- Custom exception handlers returning structured JSON errors

### AI Services
- **DistilBERT** (`facebook/bart-large-mnli` via zero-shot pipeline) — event theme classification
- **GPT-2 small** (`gpt2`) — conversation starter generation with prompt engineering
- **Wikipedia API** (`wikipedia-api` package) — fact verification

### Storage
- JSON-based local persistence in `data/` directory
- Full CRUD via `StorageService`

### Frontend (Streamlit)
- Premium dark/light theme with custom CSS
- Multi-page: Main App, Dashboard Analytics, History Browser
- Real-time API calls to FastAPI backend
- Download history as JSON/CSV

### Tests
- pytest with `httpx.AsyncClient` for endpoint testing
- `unittest.mock` to patch AI model calls
- `pytest-cov` for 90%+ coverage target

## Verification Plan

### Automated Tests
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Manual Verification
- Start FastAPI: `uvicorn app.main:app --reload`
- Start Streamlit: `streamlit run frontend/streamlit_app.py`
- Test each endpoint via Swagger UI at http://localhost:8000/docs

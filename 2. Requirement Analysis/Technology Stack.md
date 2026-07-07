# Technology Stack
## Personalized Networking Assistant

**Project:** Personalized Networking Assistant  
**Team Lead:** Shaik Sumiya Zainab  
**Version:** 1.0  
**Date:** July 2026  

---

## 1. Overview

This document describes the complete technology stack chosen for the Personalized Networking Assistant, including the rationale for each selection, version information, and role in the system.

---

## 2. Architecture Layers

```
┌──────────────────────────────────────────────────┐
│             PRESENTATION LAYER                    │
│         Streamlit 1.35+ (Python UI)               │
└──────────────────────┬───────────────────────────┘
                       │ HTTP (REST API)
┌──────────────────────▼───────────────────────────┐
│               API LAYER                           │
│          FastAPI 0.111+ + Uvicorn                 │
│         Pydantic v2 (Data Validation)             │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│             AI / SERVICE LAYER                    │
│  HuggingFace Transformers (BART + GPT-2)          │
│  Wikipedia REST API (Fact-Check)                  │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│             DATA LAYER                            │
│       Local JSON Files (history, feedback)        │
│       pathlib (cross-platform file I/O)           │
└──────────────────────────────────────────────────┘
```

---

## 3. Frontend Technologies

### Streamlit
| Property | Value |
|---|---|
| **Version** | 1.35+ |
| **Purpose** | Interactive web UI for the application |
| **Why Chosen** | Pure Python framework — no HTML/CSS/JS required; ideal for AI/ML demos; rapid prototyping |
| **Key Features Used** | `st.session_state`, `st.tabs`, `st.columns`, `st.expander`, `st.sidebar`, `st.download_button` |
| **URL** | http://localhost:8501 |

**Pages:**
- `frontend/streamlit_app.py` — Main page (Generate, Fact-Check, History tabs)
- `frontend/pages/dashboard.py` — Analytics dashboard
- `frontend/pages/history.py` — Full history browser

---

## 4. Backend Technologies

### FastAPI
| Property | Value |
|---|---|
| **Version** | 0.111+ |
| **Purpose** | RESTful API backend |
| **Why Chosen** | Automatic OpenAPI/Swagger docs; Pydantic integration; async support; best-in-class performance |
| **Key Features Used** | `APIRouter`, `Depends`, `HTTPException`, `lifespan`, CORS middleware |
| **Documentation** | http://localhost:8000/docs |

### Uvicorn
| Property | Value |
|---|---|
| **Version** | 0.30+ |
| **Purpose** | ASGI server to run FastAPI |
| **Why Chosen** | Fastest Python ASGI server; supports hot-reload with `--reload` flag |
| **Launch Command** | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |

### Pydantic v2
| Property | Value |
|---|---|
| **Version** | 2.7+ |
| **Purpose** | Data validation, serialization, settings management |
| **Why Chosen** | Automatic type checking; integrates natively with FastAPI; clear 422 error messages |
| **Key Classes** | `BaseModel`, `BaseSettings`, `Field`, `validator` |

---

## 5. AI / NLP Technologies

### HuggingFace Transformers
| Property | Value |
|---|---|
| **Version** | 4.40+ |
| **Purpose** | NLP model loading and inference pipeline |
| **Why Chosen** | Industry-standard library; supports 100,000+ pretrained models; simple `pipeline()` API |

### BART-large-mnli (Theme Extraction)
| Property | Value |
|---|---|
| **Model ID** | `facebook/bart-large-mnli` |
| **Task** | Zero-shot text classification |
| **Parameters** | ~400M parameters |
| **RAM Required** | ~1.2 GB |
| **Disk Space** | ~400 MB |
| **Why Chosen** | Best accuracy for zero-shot classification; works for any event type without fine-tuning; MNLI training gives robust semantic understanding |
| **Alternative Considered** | `cross-encoder/nli-distilroberta-base` (faster but less accurate) |

### GPT-2 Small (Conversation Generation)
| Property | Value |
|---|---|
| **Model ID** | `gpt2` |
| **Task** | Causal language modeling (text generation) |
| **Parameters** | 124M parameters |
| **RAM Required** | ~500 MB |
| **Disk Space** | ~500 MB |
| **Why Chosen** | Runs on CPU without GPU; fast inference; sufficient quality for short networking conversation starters; no API key required |
| **Alternative Considered** | `gpt2-medium` (better quality but 3× slower on CPU) |
| **Configuration** | `max_new_tokens=80`, `temperature=0.85`, `top_p=0.92`, `set_seed(42)` |

### PyTorch
| Property | Value |
|---|---|
| **Version** | 2.2+ (CPU build) |
| **Purpose** | Deep learning runtime for HuggingFace models |
| **Note** | CPU-only version used; no CUDA required |

---

## 6. External APIs

### Wikipedia REST API
| Property | Value |
|---|---|
| **Endpoint** | `https://en.wikipedia.org/api/rest_v1/page/summary/{query}` |
| **Purpose** | Topic fact-checking and quick reference |
| **Authentication** | None required (public API) |
| **Why Chosen** | Reliable, publicly accessible knowledge base; structured JSON response; no API key needed |
| **Rate Limits** | No strict limits for reasonable usage with `User-Agent` header |
| **Fallback** | Returns user-friendly error message on network failure |

---

## 7. Testing Technologies

### pytest
| Property | Value |
|---|---|
| **Version** | 8.2+ |
| **Purpose** | Unit and integration test framework |
| **Why Chosen** | De-facto standard for Python testing; fixture system; parametrize support |

### httpx + TestClient
| Property | Value |
|---|---|
| **Version** | 0.27+ |
| **Purpose** | FastAPI route testing without running a server |
| **Why Chosen** | In-process testing; zero network overhead; ships with FastAPI |

### pytest-cov
| Property | Value |
|---|---|
| **Version** | 5.0+ |
| **Purpose** | Code coverage reporting |
| **Target** | 80%+ coverage |

### unittest.mock
| Property | Value |
|---|---|
| **Source** | Python standard library |
| **Purpose** | Mocking AI model calls and external APIs in tests |
| **Why Chosen** | Eliminates GPU/internet dependency in CI/CD pipelines |

---

## 8. DevOps & Deployment Technologies

### Docker
| Property | Value |
|---|---|
| **Version** | 24.0+ |
| **Purpose** | Containerization for reproducible deployments |
| **Base Image** | `python:3.11-slim` |

### Docker Compose
| Property | Value |
|---|---|
| **Version** | 2.x |
| **Purpose** | Orchestrate backend + frontend containers |
| **Services** | `api` (FastAPI on port 8000), `frontend` (Streamlit on port 8501) |

### Git + GitHub
| Property | Value |
|---|---|
| **Purpose** | Version control and collaboration |
| **Repository** | https://github.com/Sumiyazainab2308/Personalized-Networking-Assistant |
| **Branch Strategy** | `master` branch for production-ready code |

---

## 9. Development Tools

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Primary programming language |
| Visual Studio Code / PyCharm | Latest | IDE |
| pip | 24+ | Package management |
| python-dotenv | 1.0+ | `.env` file loading |
| python-multipart | 0.0.9+ | Form data parsing in FastAPI |
| pathlib | stdlib | Cross-platform file handling |
| logging | stdlib | Application-level logging |
| threading | stdlib | Thread-safe model singleton |

---

## 10. Complete Dependencies (requirements.txt)

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
pydantic-settings==2.3.4
streamlit==1.35.0
transformers==4.40.0
torch==2.2.2
requests==2.32.3
wikipedia-api==0.6.0
python-dotenv==1.0.1
httpx==0.27.0
pytest==8.2.2
pytest-asyncio==0.23.7
pytest-cov==5.0.0
python-multipart==0.0.9
```

---

## 11. Technology Selection Summary

| Layer | Technology | Alternative Considered | Reason for Selection |
|---|---|---|---|
| Frontend | Streamlit | Flask + HTML | Python-native, no frontend code needed |
| Backend | FastAPI | Django REST, Flask | Auto-docs, Pydantic integration, speed |
| Theme Extraction | BART-large-mnli | DistilBERT, RoBERTa | Best zero-shot accuracy |
| Text Generation | GPT-2 Small | GPT-2 Medium, GPT-Neo | CPU-compatible, fast, no API key |
| Fact-Check | Wikipedia REST API | News API, Google Search | Free, no auth, structured JSON |
| Storage | JSON files | SQLite, PostgreSQL | Simplicity for MVP; easily migratable |
| Testing | pytest + httpx | unittest | Industry standard; FastAPI native |
| Deployment | Docker + Compose | Heroku, Railway | Reproducible, self-contained |

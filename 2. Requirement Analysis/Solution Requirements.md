# Solution Requirements
## Personalized Networking Assistant

**Project:** Personalized Networking Assistant  
**Team Lead:** Shaik Sumiya Zainab  
**Team Members:** Naga Jagan Mohan Rao Thattukolla, Satvika Tallam, Tejesh Velivela  
**Version:** 1.0  
**Date:** July 2026  

---

## 1. Project Overview

The Personalized Networking Assistant is an AI-powered web application that helps users generate smart, tailored conversation starters for professional or social networking events. It uses transformer-based NLP models for theme extraction and text generation, Wikipedia API for fact-checking, and provides history and feedback features for continuous improvement.

---

## 2. Functional Requirements

### FR-01: Event Theme Extraction
- **Description:** The system shall accept a plain-text event description from the user and extract the top 3 most relevant thematic categories.
- **Input:** Event description string (minimum 10 characters)
- **Output:** List of 3 theme labels (e.g., ["AI", "sustainability", "technology"])
- **Model Used:** `facebook/bart-large-mnli` (zero-shot classification)
- **Acceptance Criteria:** Returns at least 1 theme; all themes are strings; result is a list

### FR-02: Conversation Starter Generation
- **Description:** The system shall generate 2–5 personalized conversation starters based on the extracted themes and user interests.
- **Input:** Event themes (list), user bio/interests (string or list), number of starters (int)
- **Output:** List of natural language conversation starter strings
- **Model Used:** `gpt2` (GPT-2 Small, text generation)
- **Acceptance Criteria:** Returns non-empty strings; no bullet markers; starters are contextually relevant

### FR-03: Fact-Checking via Wikipedia
- **Description:** The system shall allow users to verify any topic using the Wikipedia REST API and return a summarized reference.
- **Input:** Query string (topic or claim)
- **Output:** Dictionary containing `found` (bool), `extract` (summary), `url` (Wikipedia link), `confidence` (string)
- **API Used:** `https://en.wikipedia.org/api/rest_v1/page/summary/{query}`
- **Acceptance Criteria:** Returns a dict; gracefully handles 404 and network errors; no authentication required

### FR-04: Conversation History Logging
- **Description:** Every successful conversation generation shall be automatically persisted to a local JSON file for future review.
- **Input:** Session data dictionary (event, themes, starters, timestamp)
- **Output:** Session ID (string); file `data/history.json` updated
- **Acceptance Criteria:** Atomic write; existing history preserved; timestamp auto-added if missing

### FR-05: Feedback Submission
- **Description:** Users shall be able to rate individual conversation starters with thumbs-up (👍) or thumbs-down (👎) and submit an optional 1–5 star rating and comment.
- **Input:** Suggestion text, action ("like"/"dislike"), optional session_id, rating, comment
- **Output:** Feedback entry written to `data/feedback.json`
- **Acceptance Criteria:** Feedback persisted with timestamp; existing feedback preserved

### FR-06: History Review
- **Description:** Users shall be able to view their past conversation sessions, sorted in reverse chronological order.
- **Input:** Page number, page size (default 5), optional keyword search
- **Output:** Paginated list of session records
- **Acceptance Criteria:** Returns most-recent-first; supports keyword search; returns empty list when no history

### FR-07: Feedback History View
- **Description:** Users shall be able to view the 10 most recent feedback entries with 👍/👎 icons and timestamps.
- **Input:** None (reads from `data/feedback.json`)
- **Output:** List of feedback records in reverse chronological order
- **Acceptance Criteria:** Returns at most 10 entries; icons rendered correctly; never raises exception

### FR-08: API Health Check
- **Description:** A health-check endpoint shall be available for monitoring and deployment verification.
- **Endpoint:** `GET /`
- **Output:** `{"status": "ok", "message": "API is running"}`
- **Acceptance Criteria:** Returns HTTP 200 always; responds in <100ms

---

## 3. Non-Functional Requirements

### NFR-01: Performance
- Theme extraction response time: < 5 seconds (after model warm-up)
- Conversation generation response time: < 10 seconds
- Fact-check response time: < 3 seconds (Wikipedia API)
- API health check: < 100 ms

### NFR-02: Reliability
- All API endpoints must handle malformed input gracefully with HTTP 422
- All service functions must never raise unhandled exceptions to the user
- Fact-checker must return a fallback dict on any network failure

### NFR-03: Usability
- Frontend must be accessible at `http://localhost:8501`
- Swagger UI must be available at `http://localhost:8000/docs`
- All generated starters must be displayed as clean text (no bullet markers, no raw tokens)

### NFR-04: Scalability
- The application is designed for single-user local use in MVP phase
- Architecture supports future migration to PostgreSQL/SQLite
- CORS enabled for cross-origin requests in future multi-client deployments

### NFR-05: Security
- `.env` file (containing secrets) is excluded from version control via `.gitignore`
- Only `.env.example` (template without real values) is committed
- No user data is sent to external services except Wikipedia API queries

### NFR-06: Testability
- Minimum 80% test coverage on all service modules
- All AI model calls must be mockable via `unittest.mock`
- All tests must pass without internet connection (mocked external APIs)

### NFR-07: Maintainability
- All public functions must have docstrings (Google style)
- All code must use Python type hints
- Services must follow Single Responsibility Principle (SRP)

### NFR-08: Portability
- Application must run on Windows, macOS, and Linux
- All file paths use `pathlib.Path` for cross-platform compatibility
- Docker support provided via `Dockerfile` and `docker-compose.yml`

---

## 4. System Constraints

| Constraint | Description |
|---|---|
| Python Version | Python 3.11 or higher required |
| RAM | Minimum 4 GB (8 GB recommended for AI models) |
| Storage | Minimum 10 GB free (for model downloads ~900 MB) |
| Internet | Required on first run for model download; optional thereafter |
| GPU | Not required; all inference runs on CPU |
| OS | Windows 10+, Ubuntu 20.04+, macOS 12+ |

---

## 5. API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/docs` | Swagger UI |
| POST | `/api/v1/analyze-event` | Extract themes from event description |
| POST | `/api/v1/generate-conversation` | Generate conversation starters |
| GET | `/api/v1/fact-check` | Fact-check a topic via Wikipedia |
| GET | `/api/v1/history` | Retrieve paginated session history |
| POST | `/api/v1/feedback` | Submit feedback for a session |

---

## 6. Data Requirements

| Data Entity | Storage | Format | Location |
|---|---|---|---|
| Conversation Sessions | JSON file | List of session dicts | `data/history.json` |
| User Feedback | JSON file | List of feedback dicts | `data/feedback.json` |
| AI Models | Local cache | HuggingFace format | `~/.cache/huggingface/` |
| Configuration | Environment file | Key=Value | `.env` |

---

## 7. Acceptance Criteria Summary

The system is considered complete when:
- [x] All 7 API endpoints return correct responses
- [x] BART zero-shot classification returns themes for any event description
- [x] GPT-2 generates at least 1 non-empty conversation starter
- [x] Wikipedia fact-check returns a summary or graceful fallback
- [x] History is persisted across application restarts
- [x] Feedback is persisted with timestamp
- [x] All 38 unit and integration tests pass
- [x] Streamlit UI displays all features on localhost:8501
- [x] Docker Compose starts both services successfully

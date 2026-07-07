# Data Flow Diagram
## Personalized Networking Assistant

**Project:** Personalized Networking Assistant  
**Team Lead:** Shaik Sumiya Zainab  
**Version:** 1.0  
**Date:** July 2026  

---

## 1. Overview

This document describes how data flows through the Personalized Networking Assistant system — from user input on the Streamlit frontend, through the FastAPI backend and AI service layer, to persistent storage and back to the user. Both Level 0 (Context) and Level 1 (System) DFDs are provided.

---

## 2. Level 0 DFD — Context Diagram

The Level 0 DFD shows the entire system as a single process and its external entities.

```
                    ┌──────────────────────┐
                    │                      │
    Event Desc ────►│                      │────► Conversation
    User Interests  │   PERSONALIZED       │      Starters
    Bio/Goals       │   NETWORKING         │
                    │   ASSISTANT          │────► Fact-Check Result
    Query Topic ───►│   (System)           │
                    │                      │────► Session History
    Session ID  ───►│                      │
    Feedback    ───►│                      │────► Feedback Confirmation
                    └──────────────────────┘
                              │  ▲
                              ▼  │
                    ┌──────────────────────┐
                    │   Wikipedia API      │
                    │   (External Entity)  │
                    └──────────────────────┘
```

**External Entities:**
| Entity | Type | Data Sent | Data Received |
|---|---|---|---|
| User | Primary | Event description, interests, bio, feedback | Starters, fact-check, history |
| Wikipedia API | External Service | Query string | Article extract, URL |

---

## 3. Level 1 DFD — System Decomposition

The Level 1 DFD breaks the system into its major functional processes.

```
USER
 │
 │ event_description, user_bio, num_starters
 ▼
┌────────────────────────────────────────────────────────────┐
│  Process 1: INPUT VALIDATION                                │
│  (FastAPI + Pydantic)                                       │
│  - Validate: description ≥ 10 chars                         │
│  - Validate: num_starters in [1, 10]                        │
│  - Return HTTP 422 if invalid                               │
└──────────────────────────┬─────────────────────────────────┘
                           │ validated_request
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Process 2: THEME EXTRACTION                                │
│  (event_analyzer.py / nlp_service.py)                       │
│  - Load BART-large-mnli (lazy singleton)                    │
│  - Run zero-shot classification                             │
│  - Score candidate labels against event description         │
│  - Return top-3 themes                                      │
└──────────────────────────┬─────────────────────────────────┘
                           │ themes: ["AI", "sustainability", ...]
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Process 3: CONVERSATION GENERATION                         │
│  (topic_generator.py / generation_service.py)               │
│  - Load GPT-2 Small (lazy singleton)                        │
│  - Build structured prompt from themes + bio                │
│  - Generate text (max 80 tokens)                            │
│  - Post-process: split, strip, filter                       │
│  - Return list of starters                                  │
└──────────┬───────────────────────┬─────────────────────────┘
           │ starters              │ session_data
           ▼                       ▼
    ┌──────────────┐    ┌──────────────────────────┐
    │   USER       │    │  Process 4: HISTORY LOG   │
    │  (Response)  │    │  (history_logger.py)       │
    └──────────────┘    │  - Add ISO timestamp       │
                        │  - Read history.json       │
                        │  - Append new session      │
                        │  - Write back atomically   │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │ data/        │
                              │ history.json │
                              └─────────────┘
```

---

## 4. Fact-Check Data Flow

```
USER
 │
 │ query: "blockchain in healthcare"
 ▼
┌────────────────────────────────────────────────────────────┐
│  Process 5: FACT-CHECK REQUEST                              │
│  (FastAPI Route: GET /api/v1/fact-check)                   │
│  - Validate query is not empty                              │
│  - URL-encode query string                                  │
└──────────────────────────┬─────────────────────────────────┘
                           │ encoded_query
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Process 6: WIKIPEDIA API CALL                              │
│  (fact_checker.py)                                          │
│  - GET https://en.wikipedia.org/api/rest_v1/page/summary/  │
│  - Timeout: 10 seconds                                      │
│  - Handle: 200 OK → extract text                           │
│  - Handle: 404 → not found fallback                        │
│  - Handle: Network error → error fallback                  │
└──────────────────────────┬─────────────────────────────────┘
                           │ { found, title, extract, url, confidence }
                           ▼
                    ┌─────────────────┐
                    │  USER (Response) │
                    │  ✅ Green card   │
                    │  or             │
                    │  ❌ Red fallback │
                    └─────────────────┘
```

---

## 5. Feedback Data Flow

```
USER
 │
 │ { session_id, rating, comment } OR { suggestion, action:"like"/"dislike" }
 ▼
┌────────────────────────────────────────────────────────────┐
│  Process 7: FEEDBACK SUBMISSION                             │
│  (FastAPI Route: POST /api/v1/feedback)                    │
│  - Validate: rating in [1, 5]                               │
│  - Validate: session_id exists in history                   │
└──────────────────────────┬─────────────────────────────────┘
                           │ validated_feedback
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Process 8: FEEDBACK LOG                                    │
│  (feedback_logger.py / storage_service.py)                  │
│  - Add ISO timestamp                                        │
│  - Read feedback.json                                       │
│  - Append new entry { suggestion, action, timestamp }       │
│  - Write back atomically                                    │
└──────────────────────────┬─────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │ data/feedback.json      │
              │ data/history.json       │
              │ (rating updated)        │
              └─────────────────────────┘
```

---

## 6. History Retrieval Data Flow

```
USER
 │
 │ GET /api/v1/history?page=1&page_size=5&search=AI
 ▼
┌────────────────────────────────────────────────────────────┐
│  Process 9: HISTORY RETRIEVAL                               │
│  (FastAPI Route: GET /api/v1/history)                      │
│  - Validate pagination params                               │
│  - Pass search keyword if provided                          │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │ data/          │
                   │ history.json   │
                   └───────┬───────┘
                           │ raw_records
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Process 10: FILTER & PAGINATE                              │
│  - Reverse sort (newest first)                              │
│  - Filter by keyword (if search= provided)                  │
│  - Paginate: skip=(page-1)*size, limit=size                 │
└──────────────────────────┬─────────────────────────────────┘
                           │ { items, total, page, pages }
                           ▼
                    ┌─────────────────┐
                    │  USER (Response) │
                    │  Expandable cards│
                    └─────────────────┘
```

---

## 7. Data Stores

| Data Store | ID | Location | Format | Access |
|---|---|---|---|---|
| Session History | D1 | `data/history.json` | JSON Array | Read/Write |
| User Feedback | D2 | `data/feedback.json` | JSON Array | Read/Write |
| AI Model Cache | D3 | `~/.cache/huggingface/` | Binary (HF format) | Read-only at runtime |
| App Configuration | D4 | `.env` | Key=Value | Read-only at startup |

---

## 8. Data Dictionary

### Input Data

| Field | Type | Validation | Example |
|---|---|---|---|
| `event_description` | string | min 10 chars | "AI for Sustainable Cities" |
| `user_bio` | string | optional | "Software engineer, ML enthusiast" |
| `num_starters` | int | 1–10 | 3 |
| `query` | string | min 1 char | "blockchain in healthcare" |
| `session_id` | UUID string | must exist | "abc-123-def" |
| `rating` | int | 1–5 | 4 |
| `comment` | string | optional | "Very relevant starters!" |

### Output Data

| Field | Type | Description | Example |
|---|---|---|---|
| `session_id` | string | Unique session identifier | "f47ac10b-58cc..." |
| `starters` | List[str] | Generated conversation starters | ["What's your view on AI?"] |
| `themes_used` | List[str] | Extracted themes | ["AI", "sustainability"] |
| `found` | bool | Fact-check: topic found? | true |
| `extract` | string | Wikipedia summary | "Blockchain is a distributed..." |
| `url` | string | Wikipedia article URL | "https://en.wikipedia.org/..." |
| `confidence` | string | high / medium / low | "high" |

---

## 9. Data Flow Security

| Data | Risk | Mitigation |
|---|---|---|
| `.env` file (API keys) | Exposure via git | Listed in `.gitignore`; only `.env.example` committed |
| User input | Injection | Pydantic validation rejects malformed input |
| Wikipedia response | Untrusted HTML | Only `extract` text field used; no HTML rendering |
| history.json | Concurrent write corruption | Atomic file write pattern used |
| Model weights | Unauthorized modification | Read from HuggingFace cache (read-only at runtime) |

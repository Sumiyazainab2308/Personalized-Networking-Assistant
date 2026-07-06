# Project Workflow — Personalized Networking Assistant

## Overview

This document describes the complete project workflow — from user input through AI processing to output display — for all three core scenarios supported by the application.

---

## Application Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Streamlit UI)                   │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ Event Input  │  │  Fact Check   │  │   History    │ │
│  │ + Bio/Goals  │  │   Input Box   │  │   Viewer     │ │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────┘ │
└─────────│─────────────────│────────────────── │─────────┘
          │ HTTP POST        │ HTTP GET           │ HTTP GET
          ▼                  ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend (port 8000)             │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ POST /generate  │  │ GET /fact-   │  │ GET /       │ │
│  │  -conversation  │  │    check     │  │  history   │ │
│  └────────┬────────┘  └──────┬───────┘  └─────┬──────┘ │
└───────────│──────────────────│────────────── ──│────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌───────────────────┐  ┌───────────────┐  ┌──────────────┐
│   AI Services     │  │ Fact Checker  │  │   Storage    │
│ ┌───────────────┐ │  │  (Wikipedia   │  │   Service    │
│ │ BART Zero-Shot│ │  │   REST API)   │  │  (JSON file) │
│ │ (Theme Extract)│ │  └───────────────┘  └──────────────┘
│ └───────┬───────┘ │
│         ▼         │
│ ┌───────────────┐ │
│ │   GPT-2 Small │ │
│ │ (Text Generate)│ │
│ └───────────────┘ │
└───────────────────┘
```

---

## Workflow 1: Generating Conversation Starters

**Scenario:** A user enters an event description and their interests, then clicks "Generate Starters".

### Step-by-Step Flow

```
Step 1: User Input
  └─ Event Description: "AI for Sustainable Cities"
  └─ User Interests: "climate change, urban planning"
  └─ User Bio: "Software engineer passionate about smart cities"
  └─ Click: [Generate Starters]

Step 2: Frontend → Backend API Call
  └─ POST /api/v1/generate-conversation
  └─ Payload: { event_description, user_bio, num_starters: 5 }

Step 3: Validation (FastAPI + Pydantic)
  └─ Check: description ≥ 10 characters ✅
  └─ Check: num_starters in range [1, 10] ✅
  └─ Auto-reject invalid requests with 422 error

Step 4: Theme Extraction (BART Zero-Shot)
  └─ Input: "AI for Sustainable Cities"
  └─ Candidate labels: [AI, sustainability, technology, business, ...]
  └─ Output: ["technology", "AI", "sustainability"] (top-3)

Step 5: Conversation Generation (GPT-2)
  └─ Prompt construction:
     "I am at a networking event about technology, AI, sustainability.
      My background: Software engineer passionate about smart cities.
      Here are conversation starters: 1."
  └─ GPT-2 generates text (max 80 tokens)
  └─ Post-process: split, clean, filter → 3–5 starters

Step 6: Persist to History
  └─ Save session to data/history.json
  └─ Includes: event, themes, starters, timestamp

Step 7: API Response → Frontend Display
  └─ Return: { session_id, starters, themes_used }
  └─ Display: Styled starter cards with download button
  └─ Show: Feedback buttons (👍 / 👎 per starter)
```

---

## Workflow 2: Fact Verification

**Scenario:** A user wants to verify "blockchain in healthcare" before a conference.

```
Step 1: User Input
  └─ Topic Query: "blockchain in healthcare"
  └─ Click: [Fact Check]

Step 2: Frontend → Backend API Call
  └─ GET /api/v1/fact-check?query=blockchain+in+healthcare

Step 3: Wikipedia REST API Query
  └─ URL: https://en.wikipedia.org/api/rest_v1/page/summary/blockchain_in_healthcare
  └─ Returns: JSON with title, extract, content_urls

Step 4: Response Processing
  └─ Extract first-paragraph summary
  └─ Determine confidence (high/medium/low)
  └─ Include Wikipedia article URL

Step 5: Display Result
  └─ ✅ Green card: Topic found → show summary + URL
  └─ ❌ Red card: Not found → show fallback message
```

---

## Workflow 3: Reviewing History

**Scenario:** A user wants to review past conversations and which were marked useful.

```
Step 1: User navigates to History tab / History page
  └─ Click: [History] tab in main app OR History page in sidebar

Step 2: Frontend → Backend API Call
  └─ GET /api/v1/history?page=1&page_size=5

Step 3: Storage Service Reads JSON
  └─ Reads data/history.json
  └─ Returns most recent N records (sorted by timestamp)
  └─ Supports keyword search via ?search= parameter

Step 4: Display History
  └─ Expandable cards showing:
     - Event description (truncated)
     - Themes extracted
     - Number of starters generated
     - Star rating (if feedback given)
     - First starter as preview
```

---

## Workflow 4: Submitting Feedback

**Scenario:** After generating starters, user rates them.

```
Step 1: User sees generated starters
  └─ Per-starter: 👍 Like / 👎 Dislike buttons
  └─ Overall: Star rating slider (1–5 ⭐)

Step 2: User clicks Like on a starter
  └─ feedback_logger.log_feedback(suggestion, action="like")
  └─ POST /api/v1/feedback { session_id, rating, comment }

Step 3: Feedback persisted
  └─ Saved to data/feedback.json (feedback_logger)
  └─ Rating saved to data/history.json (storage_service)

Step 4: Feedback History View
  └─ Shows last 10 rated starters
  └─ 👍 / 👎 icons with timestamps
  └─ Enables self-reflection on networking strategy
```

---

## Request Lifecycle (Technical)

```
Browser → Streamlit → requests.post() → FastAPI Router
                                              │
                                        Pydantic Validation
                                              │
                                        Orchestrator Layer
                                         ┌───┴────────────┐
                                   NLP Service     Storage Service
                                   (BART Model)    (JSON file I/O)
                                         │
                                   Generation Service
                                   (GPT-2 Model)
                                         │
                                   FastAPI Response
                                         │
                              Streamlit UI Display
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit 1.35+ | Interactive UI, session state |
| Backend | FastAPI 0.111+ | REST API, validation, routing |
| Theme Extraction | BART-large-mnli | Zero-shot event classification |
| Text Generation | GPT-2 Small | Conversation starter generation |
| Fact Checking | Wikipedia REST API | Topic verification |
| Data Storage | JSON files | Local persistence |
| Testing | pytest + httpx | Unit & integration tests |
| Containerization | Docker + Compose | Deployment |

# ER Diagram Description — Personalized Networking Assistant

## Overview

The Entity-Relationship (ER) diagram defines the logical data structure of the Personalized Networking Assistant. It models how user profiles, networking events, AI-generated content, fact-check results, and user feedback are stored and related.

The diagram consists of **6 entities** organized around the central `NETWORKING_SESSION` entity, which acts as the core session log linking all other entities together.

---

## Entity Descriptions

### 1. USER_PROFILE
**Role:** Primary entity representing a registered or active user.

| Attribute | Type | Description |
|---|---|---|
| `UserID` | UUID (PK) | Unique identifier for each user |
| `BioText` | Text | User's professional bio used for personalization |
| `currentEventCache` | Text | Cached event description from the most recent session |

**Relationships:**
- One `USER_PROFILE` can have **many** `NETWORKING_SESSION` records (1:m)
- One `USER_PROFILE` generates **many** `LOG_ENTRY` records (1:m)

---

### 2. EVENT_CONTEXT
**Role:** Stores the core event data provided by the user.

| Attribute | Type | Description |
|---|---|---|
| `EventID` | UUID (PK) | Unique identifier for each event |
| `EventDescription` | Text | Full description of the networking event |
| `AnalyzedThemes` | Text | Comma-separated themes extracted by BART classifier |

**Relationships:**
- One `EVENT_CONTEXT` is associated with **many** `NETWORKING_SESSION` records (1:m)

---

### 3. GENERATED_STARTER
**Role:** Stores the AI-generated conversation starters (resulting chat prompts).

| Attribute | Type | Description |
|---|---|---|
| `StarterID` | UUID (PK) | Unique identifier for each starter |
| `SessionID` | UUID (FK) | References the `NETWORKING_SESSION` that produced this starter |
| `StarterText` | Text | The generated conversation starter sentence |
| `ContextPromptUsed` | Text | The GPT-2 prompt that generated this starter |

**Relationships:**
- One `NETWORKING_SESSION` produces **many** `GENERATED_STARTER` records (1:m)

---

### 4. NETWORKING_SESSION
**Role:** The core session log — central entity linking all others.

| Attribute | Type | Description |
|---|---|---|
| `SessionID` | UUID (PK) | Unique identifier for each session |
| `UserID` | UUID (FK) | References `USER_PROFILE` |
| `EventID` | UUID (FK) | References `EVENT_CONTEXT` |
| `SessionTimestamp` | DateTime | UTC timestamp when session was created |

**Relationships:**
- Links `USER_PROFILE` ↔ `EVENT_CONTEXT` (many-to-many bridge)
- One `NETWORKING_SESSION` has **many** `GENERATED_STARTER` records (1:m)
- One `NETWORKING_SESSION` has **many** `LOG_ENTRY` audit records (1:m)
- One `NETWORKING_SESSION` may have **many** `WIKIPEDIA_FACT_CHECK` results (1:m)

---

### 5. LOG_ENTRY
**Role:** Audit log for tracking all system actions (for auditing and analytics).

| Attribute | Type | Description |
|---|---|---|
| `LogID` | UUID (PK) | Unique identifier for each log entry |
| `SessionID` | UUID (FK) | References the associated `NETWORKING_SESSION` |
| `ActionType` | Enum | Type of action (e.g., `generate_starter`, `fact_check`, `feedback`) |
| `PayloadJSON` | JSON | Full request/response payload for the action |
| `Timestamp` | DateTime | UTC timestamp of the action |

**Relationships:**
- Many `LOG_ENTRY` records belong to one `USER_PROFILE` (m:1)
- Many `LOG_ENTRY` records belong to one `NETWORKING_SESSION` (m:1)

---

### 6. WIKIPEDIA_FACT_CHECK
**Role:** Stores fact-check results from Wikipedia API queries.

| Attribute | Type | Description |
|---|---|---|
| `FactCheckID` | UUID (PK) | Unique identifier for each fact-check |
| `SessionID` | UUID (FK) | References the `NETWORKING_SESSION` that triggered the check |
| `VerifiedQueryText` | Text | The topic or claim submitted for verification |
| `VerificationStatus` | Boolean | `true` if Wikipedia found a match, `false` otherwise |
| `WikipediaSource` | Text | Wikipedia article URL returned |
| `Summary` | Text | Extracted first-paragraph summary from Wikipedia |
| `Confidence` | Enum | Confidence level: `high`, `medium`, or `low` |

**Relationships:**
- Many `WIKIPEDIA_FACT_CHECK` records link to one `NETWORKING_SESSION` (m:1)

---

## Entity Relationship Summary

```
USER_PROFILE  ──(1:m)──  NETWORKING_SESSION  ──(1:m)──  GENERATED_STARTER
                  │
                  ├──(m:1)──  EVENT_CONTEXT
                  │
                  ├──(1:m)──  LOG_ENTRY
                  │
                  └──(1:m)──  WIKIPEDIA_FACT_CHECK
```

---

## Design Decisions

1. **No Database in MVP:** All entities are persisted as JSON files (`data/history.json`, `data/feedback.json`) in the current implementation. The ER diagram models the logical structure — a future version can migrate to SQLite or PostgreSQL without changing the application logic.

2. **NETWORKING_SESSION as Hub:** The session entity bridges users and events, ensuring one user can attend many events and one event can be attended by multiple users in future multi-user scenarios.

3. **LOG_ENTRY for Auditability:** Separating audit logs from session data follows the CQRS (Command Query Responsibility Segregation) pattern, keeping business data clean while maintaining a complete audit trail.

4. **WIKIPEDIA_FACT_CHECK Decoupled:** Fact-checking is deliberately separate from conversation generation, reflecting the application's two independent features.

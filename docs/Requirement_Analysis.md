# Requirement Analysis: Personalized Networking Assistant

> [!IMPORTANT]
> **Competition Submission Document**  
> This specification defines the architectural, functional, and user-centric requirements for the **Personalized Networking Assistant**, developed for industry and academic GenAI/ML competitions. Every requirement outlined herein reflects the actual implemented system architecture, emphasizing MVP constraints and production-ready engineering practices.

---

## 1. Project Overview

The **Personalized Networking Assistant** is an artificial intelligence application designed to empower professionals, researchers, and students by generating tailored, context-aware conversation starters and networking strategies. In high-stakes professional environments—such as tech conferences, academic summits, and industry mixers—individuals frequently struggle to initiate meaningful dialogue. Traditional networking advice is overly generic, ignoring both the specific thematic context of the event and the unique background of the attendee.

To solve this challenge, our engineering team has developed an end-to-end AI/ML solution that combines Generative AI, Natural Language Processing (NLP), and real-time fact verification. Built with a **FastAPI** backend and an interactive **Streamlit** multi-page frontend, the application leverages open-source Hugging Face models (**BART-large-mnli** for zero-shot theme classification and **GPT-2 Small** for personalized text generation) running locally on CPU. To ensure conversational integrity and prevent LLM hallucinations, the system incorporates a live **Wikipedia REST API** fact-checking pipeline.

### Team Contributions & Leadership
* **Shaik Sumiya Zainab (Team Lead):** Backend architecture, FastAPI routing and orchestration, CI/CD pipeline integration, Docker containerization, and system design.
* **Naga Jagan Mohan Rao Thattukolla:** AI/ML pipeline engineering, Hugging Face model integration (BART & GPT-2), prompt engineering, zero-shot label evaluation, and text post-processing algorithms.
* **Satvika Tallam:** Quality Assurance (QA) leadership, test engineering (38 comprehensive pytest unit and integration tests), offline mocking frameworks, and test coverage optimization (≥80%).
* **Tejesh Velivela:** Streamlit frontend development, multi-page tabbed UI design, interactive feedback widgets, DevOps (Docker Compose, Makefile), and technical documentation.

---

## 2. Problem Statement

In professional networking environments, initiating conversations that are both engaging and contextually relevant is a significant barrier for attendees. Existing digital tools and general advice fail to bridge the gap between abstract event descriptions and personal networking goals. 

The core problem can be decomposed into three primary deficiencies:

1. **Generic Networking Advice:** Traditional guides provide one-size-fits-all icebreakers (e.g., *"What brings you to this event?"* or *"What do you do?"*). These static phrases fail to stimulate professional engagement or demonstrate domain knowledge.
2. **Lack of Contextual Alignment:** Attendees frequently attend specialized conferences (e.g., AI for Sustainable Urban Development, FinTech Blockchain Summits, Healthcare Telemedicine Forums). Without analyzing the specific themes of the event alongside the user's professional background (bio and interests), conversation starters feel disconnected and superficial.
3. **Hallucinated or Unverified Claims:** When attendees attempt to use general-purpose Large Language Models (LLMs) to generate talking points or industry facts, they risk relying on hallucinated or outdated information. Presenting incorrect technical facts or fabricated industry trends during networking interactions severely damages professional credibility.

---

## 3. Existing Problems & Limitations of Current Approaches

| Problem Area | Traditional Approaches | General-Purpose LLMs (e.g., Web ChatGPT) | Personalized Networking Assistant (Our Solution) |
| :--- | :--- | :--- | :--- |
| **Context Awareness** | Zero context; relies entirely on memorized scripts or generic pleasantries. | High context if manually prompted, but requires lengthy, repetitive prompt engineering by the user. | **Automated Context Merging:** Automatically extracts event themes via zero-shot classification and fuses them with user bios. |
| **Fact Verification** | Relies on personal memory; high risk of misremembering industry facts. | Prone to hallucinations; confidently generates plausible but false statistics and historical details. | **Integrated Fact-Checking:** Live verification against the Wikipedia REST API with automated confidence scoring (`verified`/`unverified`). |
| **Data Privacy & Security** | Safe (internal mental process), but digital notes may lack structured storage. | Cloud-dependent; user professional data and networking targets are transmitted to external proprietary providers. | **100% Local Inference:** CPU-based model execution with local atomic JSON persistence; zero external LLM data sharing. |
| **Latency & Accessibility** | N/A | High latency during peak network hours; requires continuous high-speed internet access. | **Optimized Local CPU Execution:** Lazy-loaded singleton model architecture ensures rapid, offline-capable inference. |
| **Feedback & Adaptation** | No structured mechanism to track which conversation starters were successful. | Chat history is linear and unstructured; difficult to perform analytics on networking success. | **Structured Feedback & Analytics:** Multi-page UI with explicit 👍/👎 buttons, star ratings, and historical trend dashboards. |

---

## 4. Proposed Solution

The **Personalized Networking Assistant** replaces static networking scripts and hallucinated AI responses with an integrated, locally hosted AI workflow. 

```
[User Input: Event Desc & Bio] 
       │
       ▼
[FastAPI Backend: /api/v1/generate-conversation]
       │
       ├─► [NLP Service: BART-large-mnli Zero-Shot Classification] ─► [Top 3 Themes]
       │                                                                    │
       └─► [Generation Service: GPT-2 Small + Prompt Engineering] ◄─────────┘
       │
       ▼
[Post-Processing: Bullet Stripping & Truncation Cleanup]
       │
       ├─► [Fact-Checker Service: Wikipedia REST API] ─► [Confidence Score & Summary]
       │
       ▼
[Atomic JSON Persistence: history.json & feedback.json]
       │
       ▼
[Streamlit Multi-Page UI: Interactive Display, Star Ratings & Analytics]
```

### Key Architectural Pillars
1. **Intelligent Theme Extraction:** Uses `facebook/bart-large-mnli` to evaluate unstructured event descriptions against candidate domain labels (`tech`, `business`, `sustainability`, `healthcare`, `finance`, `AI`, `networking`, `innovation`). The system dynamically selects the top 3 most relevant themes.
2. **Context-Aware Starter Generation:** Uses `gpt2` (124M parameters) guided by custom prompt templates that merge the extracted themes with the user's professional bio. A robust post-processing pipeline cleans raw text, strips conversational bullet markers, and repairs truncated sentences.
3. **Real-Time Fact Verification:** Provides a dedicated fact-checking engine querying `https://en.wikipedia.org/api/rest_v1/page/summary/{query}` with custom User-Agent headers, fallback defensive mechanisms, and confidence evaluation (`high`, `medium`, `low` mapped to `verified`/`unverified`).
4. **Lightweight Local Persistence:** Adopts local atomic JSON file storage (`data/history.json`, `data/feedback.json`, `data/profiles.json`) utilizing `pathlib.Path`, UUIDv4 session identifiers, and ISO-8601 UTC timestamps. This fulfills all MVP storage requirements without SQL database overhead.

---

## 5. Objectives

### 5.1 Technical Objectives
* **Local CPU Inference:** Implement lightweight NLP models capable of executing efficiently on standard laptop CPUs without requiring dedicated GPUs or external proprietary API keys.
* **High System Reliability:** Build a defensive backend using FastAPI and Pydantic v2 schemas that validates all incoming requests, handles external API failures gracefully, and guarantees 100% application stability under error conditions.
* **Comprehensive Test Coverage:** Maintain an exhaustive test suite of at least 38 pytest unit and integration tests across all core services and API routes, achieving ≥80% code coverage with offline mocking.
* **Containerized Deployment:** Ensure seamless reproducibility across diverse operating systems (Windows, macOS, Linux) via multi-stage Docker builds and automated Docker Compose orchestration.

### 5.2 User-Centric Objectives
* **Eliminate Networking Anxiety:** Provide professionals and students with tailored, highly relevant talking points within seconds of entering an event description.
* **Ensure Information Accuracy:** Protect user credibility by allowing instant verification of technical terms, concepts, and industry topics via verified Wikipedia summaries.
* **Track Networking Progress:** Enable users to review historical sessions, filter past conversations by keyword, export data to CSV/JSON, and track networking effectiveness via interactive visual analytics.

---

## 6. Scope

### 6.1 In-Scope (Implemented Features)
* **Health & Status Monitoring:** Root and health check endpoints reporting uptime and lazy-loaded model status.
* **Event Description Analysis:** REST API endpoint extracting top 3 domain themes from text descriptions up to 2000 characters.
* **Conversation Starter Generation:** End-to-end generation endpoint producing 1 to 10 customized starters based on event themes and user bios.
* **Real-Time Fact-Checking:** Query endpoint verifying concepts against Wikipedia, returning extracts, source URLs, and confidence scores.
* **Session History Management:** Retrieval endpoint supporting paginated listing, keyword searching, and session deduplication.
* **Feedback & Rating System:** Interactive submission of 1–5 star ratings and textual comments linked to specific session UUIDs.
* **Analytics Dashboard:** Aggregation endpoint computing total sessions, average ratings, theme distributions, and daily usage frequency.
* **Data Export:** Endpoints generating downloadable JSON and CSV reports of historical networking sessions.
* **Multi-Page Streamlit Frontend:** Interactive user interface featuring tabbed navigation: Generate Starters, Fact-Check, History Review, and Analytics Dashboard.

### 6.2 Out-of-Scope (Current MVP Architectural Limitations)
> [!NOTE]
> To maintain a lightweight, locally deployable footprint suitable for competition evaluation, several enterprise features are explicitly deferred to future releases.

* **SQL/NoSQL Database Integration:** The system currently utilizes local atomic JSON files (`history.json`, `feedback.json`). Enterprise database engines (PostgreSQL, MongoDB) are out of scope for the MVP.
* **User Login & Multi-User Authentication:** The application operates in a single-tenant local mode. There is no JWT authentication, OAuth2 login, or multi-user profile isolation.
* **Email & Calendar Sync:** Automated ingestion of event descriptions from Google Calendar, Outlook, or email invitations is not implemented; users manually input or paste event descriptions.
* **CRM & LinkedIn Integration:** Direct export of networking contacts or conversation notes into external CRM platforms (Salesforce, HubSpot) or social networks is out of scope.
* **GPU-Accelerated Inference & Large LLMs:** The system is constrained to CPU execution using models under 500M parameters (`gpt2` 124M, `bart-large-mnli`). Multi-billion parameter models (Llama 3, Mistral 7B) requiring GPU VRAM or cloud hosting are excluded from the current release.

---

## 7. Stakeholders

| Stakeholder Role | Representative / Target Group | Key Interests & Responsibilities |
| :--- | :--- | :--- |
| **Project Lead & Architecture Lead** | Shaik Sumiya Zainab | System reliability, clean architecture, API contract design, CI/CD automation, and overall project delivery. |
| **AI/ML Specialist** | Naga Jagan Mohan Rao Thattukolla | Model selection, zero-shot classification accuracy, prompt engineering efficacy, post-processing cleanliness, and CPU inference latency. |
| **Quality Assurance Lead** | Satvika Tallam | Test framework architecture, 100% pass rate across 38 unit/integration tests, offline mocking reliability, and code coverage metrics. |
| **Frontend & DevOps Engineer** | Tejesh Velivela | Streamlit UI/UX responsiveness, multi-page state management, Docker container optimization, and documentation clarity. |
| **End Users (Primary)** | Professionals, Researchers, Students | Rapid access to relevant conversation starters, intuitive UI navigation, fact-checking accuracy, and historical session tracking. |
| **Competition Evaluators** | Academic & Industry Judges | Codebase cleanliness, architectural rigor, adherence to AI engineering best practices, documentation depth, and test verification. |

---

## 8. User Personas

### Persona 1: Alex Chen — The Introverted Junior Software Engineer
![Screenshot Placeholder: Profile View Alex Chen](../images/placeholder_alex.png)
* **Background:** 24 years old, recently graduated with a B.S. in Computer Science. Currently working as a Junior Backend Developer at a mid-sized financial technology startup.
* **Goals:** Wants to build a professional network, find tech mentors, and learn about emerging software engineering practices at local tech meetups and developer conferences.
* **Pain Points:** Extremely introverted and anxious in social settings. Struggles to initiate conversations with senior engineers or CTOs. Fears saying something technically incorrect or sounding inexperienced.
* **How the System Helps:** Alex inputs his bio (*"Junior backend developer working with Python and APIs"*) and the event description (*"Annual Cloud Native & Kubernetes Summit"*). The app generates tailored technical starters (e.g., *"What are your thoughts on managing stateful workloads in Kubernetes?"*). Alex uses the Fact-Check tab to verify technical terms before approaching senior attendees.

### Persona 2: Sarah Jenkins — The Experienced Tech Founder & Business Developer
![Screenshot Placeholder: Profile View Sarah Jenkins](../images/placeholder_sarah.png)
* **Background:** 38 years old, Founder and CEO of an AI-driven supply chain analytics startup. Attends 2–3 major industry summits, venture capital mixers, and trade shows every month.
* **Goals:** Identify potential enterprise clients, connect with venture capital investors, and explore strategic partnerships in sustainability and logistics.
* **Pain Points:** Lacks time to research every attendee or niche topic before conferences. Needs high-level, business-oriented conversation starters that bridge technology and commercial ROI. Must track which pitches and networking angles resonated during past events.
* **How the System Helps:** Sarah generates talking points focusing on business and sustainability themes. After her meetings, she logs into the History tab, searches for *"logistics"*, and reviews past starters. She uses the 👍/👎 feedback buttons and 5-star ratings to mark which starters led to successful investor meetings, viewing her success trends on the Analytics Dashboard.

### Persona 3: Dr. Marcus Vance — The Academic Researcher Transitioning to Industry
![Screenshot Placeholder: Profile View Dr Marcus Vance](../images/placeholder_marcus.png)
* **Background:** 31 years old, Postdoctoral Researcher in Computational Biology and Bioinformatics. Presenting his research at interdisciplinary conferences bridging academic medicine and commercial biotech.
* **Goals:** Transition from academia into an industry role (Senior Data Scientist or Research Engineer) at a pharmaceutical or biotech company.
* **Pain Points:** Accustomed to highly specialized academic jargon; struggles to translate his research into accessible conversation starters for corporate recruiters and product managers. Unsure how to navigate commercial healthcare topics.
* **How the System Helps:** Dr. Vance inputs his complex academic bio and the event description for an industry healthcare summit. The system extracts themes like `healthcare`, `AI`, and `innovation`, generating accessible, industry-bridging starters. He uses the Fact-Check tab to quickly summarize commercial biotech terminology and FDA regulation concepts before networking sessions.

---

## 9. User Stories

The application's functionality is driven by the following structured user stories:

```
+-----------------------------------------------------------------------------------+
|                           USER STORY MAPPING MATRIX                               |
+-----------------------------------------------------------------------------------+
|  EPIC 1: Analysis & Generation           |  EPIC 2: Verification & History        |
|  -------------------------------------   |  ------------------------------------  |
|  US-01: Extract Event Themes             |  US-04: Fact-Check Industry Concepts   |
|  US-02: Generate Personalized Starters   |  US-05: Review Historical Sessions     |
|  US-03: Customize Starter Count          |  US-06: Search & Filter History        |
+-----------------------------------------------------------------------------------+
|  EPIC 3: Feedback & Analytics            |  EPIC 4: System & Export               |
|  -------------------------------------   |  ------------------------------------  |
|  US-07: Rate Conversation Starters       |  US-09: Export History to CSV/JSON     |
|  US-08: View Analytics Dashboard         |  US-10: Monitor System Health          |
+-----------------------------------------------------------------------------------+
```

* **US-01 (Theme Extraction):** *As a* conference attendee, *I want* the system to analyze my event description and identify the top domain themes, *so that* I understand the primary focus areas of the gathering without manually reading lengthy brochures.
* **US-02 (Personalized Generation):** *As an* introverted professional, *I want* the application to merge my personal professional bio with the event themes to generate tailored conversation starters, *so that* I can initiate meaningful dialogues that highlight my relevant experience.
* **US-03 (Customizable Count):** *As a* power user, *I want* to specify the exact number of conversation starters to generate (between 1 and 10), *so that* I can get a quick icebreaker for a small meetup or an extensive list for a multi-day summit.
* **US-04 (Fact Verification):** *As a* networking professional, *I want* to check unfamiliar concepts or technical terms against Wikipedia in real time, *so that* I can verify industry facts and avoid making incorrect statements during professional conversations.
* **US-05 (History Review):** *As a* frequent conference attendee, *I want* to browse a paginated history of all my past networking sessions, *so that* I can revisit conversation starters and themes from previous events.
* **US-06 (Keyword Search):** *As a* business developer, *I want* to search my historical sessions by keyword or theme, *so that* I can quickly locate talking points I used at specific summits or regarding specific industries.
* **US-07 (Feedback Submission):** *As an* active user, *I want* to rate generated conversation starters on a 1–5 star scale and submit thumbs-up/thumbs-down feedback with comments, *so that* I can record which strategies were effective and help refine my networking log.
* **US-08 (Analytics Dashboard):** *As a* data-conscious professional, *I want* to view visual bar charts and summary metrics of my networking history (total sessions, average rating, theme frequency), *so that* I can analyze my networking patterns over time.
* **US-09 (Data Export):** *As a* researcher, *I want* to export my networking history and feedback logs into CSV and JSON formats, *so that* I can perform offline analysis or backup my professional data.
* **US-10 (System Health Monitoring):** *As a* systems administrator or developer, *I want* to query a health check endpoint to verify API uptime and check whether AI models are loaded in memory, *so that* I can ensure reliable application performance.

---

## 10. Functional Requirements

The system implements 12 distinct functional requirements across its backend and frontend architectures:

| Req ID | Feature Name | Associated Module / Route | Detailed Functional Description |
| :--- | :--- | :--- | :--- |
| **FR-01** | **Health & Uptime Reporting** | `GET /health`<br>`GET /` | The system must provide an unauthenticated health endpoint returning application status (`ok`), version string, server uptime in seconds, and a boolean mapping of lazy-loaded AI models (`zero_shot_classifier`, `text_generator`). |
| **FR-02** | **Zero-Shot Theme Extraction** | `POST /api/v1/analyze-event`<br>`event_analyzer.py` | The system must accept an `event_description` (10–2000 chars) and optional `user_bio`, execute zero-shot classification against 8 domain labels, and return the top 3 themes sorted by confidence score alongside a unique UUIDv4 `session_id`. |
| **FR-03** | **Conversation Starter Generation** | `POST /api/v1/generate-conversation`<br>`topic_generator.py` | The system must accept an event description, user bio, optional pre-computed themes, and `num_starters` (1–10). It must construct a prompt, execute GPT-2 text generation, clean the output, and return a list of starter strings. |
| **FR-04** | **Post-Processing Text Cleanup** | `generation_service.py` | The system must process raw LLM output by splitting text into lines, stripping bullet points (e.g., `1.`, `*`, `-`), removing blank lines, filtering repetitive phrases, and repairing incomplete/truncated sentences. |
| **FR-05** | **Real-Time Fact Verification** | `GET /api/v1/fact-check`<br>`fact_checker.py` | The system must accept one or more `query` parameters, deduplicate them, query the Wikipedia REST API with a custom User-Agent, and return a structured list containing extract text, page URL, and confidence scoring (`verified`/`unverified`). |
| **FR-06** | **Paginated History Retrieval** | `GET /api/v1/history`<br>`history.py` | The system must retrieve stored networking sessions from local JSON storage, supporting pagination via `page` (≥1) and `page_size` (1–100, default 10) parameters, returning total count and session arrays. |
| **FR-07** | **Historical Keyword Search** | `GET /api/v1/history`<br>`storage_service.py` | The system must support an optional `search` query parameter on the history endpoint, performing case-insensitive substring matching across event descriptions, themes, and generated starters. |
| **FR-08** | **Feedback & Star Rating Logging** | `POST /api/v1/feedback`<br>`feedback_logger.py` | The system must accept feedback payloads containing a valid `session_id`, an integer `rating` (1–5), optional `starter_index`, and optional text `comment`, persisting updates directly to the corresponding session record. |
| **FR-09** | **Analytics Data Aggregation** | `GET /api/v1/history/analytics`<br>`history.py` | The system must aggregate historical data and compute total session count, overall average feedback rating, theme frequency distribution maps, and daily session activity volume. |
| **FR-10** | **Session Data Export** | `GET /api/v1/history/export/csv`<br>`.../export/json` | The system must allow downloading the entire session history as a structured JSON array (`application/json`) or a comma-separated values file (`text/csv`) with appropriate content-disposition headers. |
| **FR-11** | **Thread-Safe Atomic Persistence** | `storage_service.py` | The system must persist all session and feedback records to local JSON files (`data/history.json`, `data/feedback.json`) using thread-safe file locking and atomic write operations (write-to-temp and rename). |
| **FR-12** | **Multi-Page Tabbed UI** | `streamlit_app.py`<br>`dashboard.py`, `history.py` | The system must render a Streamlit web interface featuring tabbed navigation: **Generate Starters** (with dynamic 👍/👎 and rating buttons), **Fact-Check** (interactive query input), **History** (search/pagination tables), and **Analytics** (bar charts). |

---

## 11. Non-Functional Requirements

### 11.1 Performance & Latency
* **CPU Inference Bounds:** Because the system executes on CPU without GPU acceleration, AI inference must be optimized. Zero-shot theme classification (`bart-large-mnli`) must complete within **3.0 to 5.0 seconds** for standard descriptions. Text generation (`gpt2`) must complete within **2.0 to 4.0 seconds** for 5 conversation starters.
* **API Response Times:** Non-ML endpoints (`GET /health`, `GET /api/v1/history`, `POST /api/v1/feedback`) must respond in **<100 milliseconds**.
* **UI Responsiveness:** Streamlit UI state transitions and tab switching must render within **<200 milliseconds**.

### 11.2 Reliability & Fault Tolerance
* **Defensive Fact-Checking Fallbacks:** External network calls to the Wikipedia REST API must implement a strict 10-second timeout. If the external API returns 404, rate-limits (429), or drops connectivity, the system must **never raise an unhandled exception**. It must return a defensive fallback payload (`found=False`, `confidence='unverified'`, with an appropriate user explanation).
* **Atomic Storage Consistency:** To prevent data corruption during simultaneous writes or unexpected shutdowns, storage operations must write data to a temporary file before atomically renaming it to the target JSON file.
* **100% Test Pass Rate:** All 38 pytest unit and integration tests must pass deterministically in CI/CD environments without requiring internet connectivity or local GPU hardware.

### 11.3 Usability & Accessibility
* **Intuitive Navigation:** The frontend must organize functionality into clean, self-explanatory tabs with clear typography and professional formatting.
* **Graceful Error Messaging:** When user inputs violate schema boundaries (e.g., event descriptions shorter than 10 characters or ratings outside 1–5), the API and UI must return clear, human-readable validation messages rather than raw stack traces.
* **Visual Data Presentation:** Analytics must be presented via clear visual bar charts and metric cards to facilitate rapid scannability.

### 11.4 Security & Privacy
* **100% Local Data Processing:** All event descriptions, user bios, and generated conversation starters are processed entirely on the local host machine. Zero proprietary user data is transmitted to external commercial LLM APIs (e.g., OpenAI, Anthropic).
* **Environment Variable Isolation:** Sensitive system configuration and model parameters must be managed strictly via environment variables loaded through `pydantic-settings`, utilizing `.env` files that are excluded from version control via `.gitignore`.
* **Input Sanitization:** All textual inputs must be validated via Pydantic v2 schemas and sanitized to prevent injection attacks or malformed payload corruption.

---

## 12. Assumptions & Constraints

### 12.1 Assumptions
* **Operating Environment:** The end-user or evaluator is running a modern operating system (Windows 10/11, macOS, or Linux) with Python 3.9+ installed, or has Docker and Docker Compose installed for containerized execution.
* **Language Support:** All event descriptions, user bios, and networking queries are inputted in the English language. Open-source models (`bart-large-mnli` and `gpt2`) are evaluated primarily on English text.
* **Network Connectivity for Fact-Checking:** While AI inference is 100% offline and local, the **Fact-Check** feature assumes an active internet connection to query `https://en.wikipedia.org/api/rest_v1/`. If offline, the system safely degrades to fallback messages.

### 12.2 Constraints (MVP Architectural Boundaries)
```
+-----------------------------------------------------------------------------------+
|                        MVP ARCHITECTURAL CONSTRAINTS                              |
+-----------------------------------------------------------------------------------+
|  1. CPU-Only Execution       |  No GPU required; constrained to models <500M      |
|                              |  params (GPT-2 Small 124M, BART-large-mnli).       |
|  ----------------------------+--------------------------------------------------  |
|  2. Atomic JSON Storage      |  No SQL/NoSQL database server; data persisted to   |
|                              |  local files (history.json, feedback.json).        |
|  ----------------------------+--------------------------------------------------  |
|  3. Single-Tenant Mode       |  No user login, JWT auth, or multi-user profile    |
|                              |  isolation implemented in current release.         |
|  ----------------------------+--------------------------------------------------  |
|  4. Synchronous API Polling  |  No WebSocket or WebRTC real-time streaming;       |
|                              |  frontend communicates via REST HTTP requests.     |
+-----------------------------------------------------------------------------------+
```

---

## 13. Success Criteria

The Personalized Networking Assistant project is evaluated against strict technical and functional criteria:

1. **Test Suite Verification:** The automated test suite (`pytest`) must achieve a **100% pass rate across all 38 unit and integration tests** located in `test_event_analyzer.py`, `test_topic_generator.py`, `test_fact_checker.py`, and the API test suite (`test_analyze.py`, `test_factcheck.py`, `test_feedback.py`, `test_generate.py`, `test_history.py`), with code coverage exceeding **80%**.
2. **Functional Completeness:** All 7 REST API endpoints and all 4 Streamlit UI tabs must function seamlessly without runtime errors, fulfilling all 12 Functional Requirements.
3. **Inference Stability:** The lazy-loaded singleton AI models must load successfully on standard CPU hardware without memory leaks or out-of-memory (OOM) crashes during continuous multi-session testing.
4. **Data Persistence Integrity:** Session logs, star ratings, and comments must persist accurately across server restarts without data loss or JSON file corruption.
5. **Quality of Generated Output:** Post-processing algorithms must guarantee that 100% of generated conversation starters returned to the user are free of bullet markers, empty strings, and awkward sentence truncations.

---

> [!TIP]
> **Next Steps for Evaluators:**  
> Proceed to `System_Design.md` to review the comprehensive component diagrams, data flow architectures, and technology stack justifications.

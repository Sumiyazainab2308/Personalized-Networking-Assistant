# Implementation & DevOps Guide: Personalized Networking Assistant

> [!IMPORTANT]
> **Competition Submission Document**  
> This document provides an in-depth code engineering and DevOps walkthrough for the **Personalized Networking Assistant**. It details backend FastAPI routing, Streamlit frontend state management, dynamic UI key generation, Pydantic v2 configuration, environment variable schemas, local development workflows, and Docker containerization.

---

## 1. Backend Architecture & Engineering (FastAPI)

The backend application server is constructed using **FastAPI 0.109+**, structured to ensure strict type safety, asynchronous request handling, and modular routing.

### 1.1 Application Factory & Lifecycle (`app/main.py`)
The application utilizes an asynchronous lifecycle context manager (`lifespan`) to log startup metadata and cleanly manage resource teardown without blocking the ASGI event loop:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info("Starting %s v%s | debug=%s", settings.app_name, settings.app_version, settings.debug)
    yield
    logger.info("Shutting down %s.", settings.app_name)
```

The application factory `create_app()` instantiates the FastAPI server and attaches two critical middleware layers:
1. **`CORSMiddleware`:** Restricts cross-origin requests using `settings.allowed_origins` (parsed from `ALLOWED_ORIGINS_STR` in `.env`), enabling secure communication with the Streamlit frontend on port 8501.
2. **Request Logging Middleware:** An `@app.middleware("http")` function intercepts every incoming HTTP request, records start time via `time.perf_counter()`, executes the route handler, and logs the HTTP method, URL path, status code, and exact millisecond duration.

### 1.2 Global Exception Handling & Defensive Design
To guarantee that the backend **never returns raw stack traces or HTML 500 pages**, `main.py` registers structured JSON exception handlers:
* **`AppBaseException` Handler:** Catches all domain-specific application exceptions (e.g., validation failures, storage locking conflicts), converting them into standardized `ErrorResponse` Pydantic JSON payloads with appropriate HTTP status codes (400, 404, 422).
* **Catch-All `Exception` Handler:** Wraps any unexpected runtime errors (e.g., sudden OOM conditions) in an `InternalServerError` JSON structure, logging the full stack trace to disk while returning a clean 500 error message to the client.

### 1.3 Modular Routing & Dependency Injection
To prevent monolithic controller files, API endpoints are partitioned across domain routers in `app/routers/` and mounted under the `/api/v1` prefix:
* `analyze.py` $\rightarrow$ `POST /api/v1/analyze-event`
* `generate.py` $\rightarrow$ `POST /api/v1/generate-conversation`
* `factcheck.py` $\rightarrow$ `GET /api/v1/fact-check`
* `history.py` $\rightarrow$ `GET /api/v1/history`, `/analytics`, `/export/json`, `/export/csv`
* `feedback.py` $\rightarrow$ `POST /api/v1/feedback`

Route handlers leverage FastAPI's dependency injection system (e.g., `Depends(get_settings)`) to cleanly inject configuration singletons and service wrappers without global state entanglement.

---

## 2. API Layer Specification

The application exposes 7 core REST API endpoints (plus associated analytics and export routes), fully documented via automatic OpenAPI/Swagger UI (`/docs`).

```
+-----------------------------------------------------------------------------------+
|                        REST API ENDPOINT SPECIFICATION                            |
+-----------------------------------------------------------------------------------+
|  Method  |  Endpoint Path                  |  Description & Core Functionality    |
+----------+---------------------------------+--------------------------------------+
|  GET     |  /health                        |  Returns system health & model status|
|  POST    |  /api/v1/analyze-event          |  Extracts top 3 themes via BART NLI  |
|  POST    |  /api/v1/generate-conversation  |  Generates starters via GPT-2 & bio  |
|  GET     |  /api/v1/fact-check             |  Verifies concepts against Wikipedia |
|  GET     |  /api/v1/history                |  Paginated & searchable session log  |
|  POST    |  /api/v1/feedback               |  Logs 1-5 star ratings & comments    |
|  GET     |  /api/v1/history/analytics      |  Aggregates metrics for UI dashboard |
|  GET     |  /api/v1/history/export/json    |  Exports session log as JSON file    |
|  GET     |  /api/v1/history/export/csv     |  Exports session log as CSV file     |
+-----------------------------------------------------------------------------------+
```

### 2.1 Key Request & Response Pydantic Schemas (`app/models/`)
All payloads are strictly enforced via Pydantic v2 models:

* **`GenerateConversationRequest`:**
  ```python
  class GenerateConversationRequest(BaseModel):
      event_description: str = Field(..., min_length=10, max_length=2000)
      user_bio: Optional[str] = Field(None, max_length=1000)
      themes: Optional[list[str]] = None
      num_starters: int = Field(5, ge=1, le=10)
  ```
* **`GenerateConversationResponse`:**
  ```python
  class GenerateConversationResponse(BaseModel):
      session_id: str
      timestamp: str
      event_description: str
      user_bio: Optional[str]
      themes_used: list[str]
      starters: list[str]
  ```

---

## 3. Authentication & Security Architecture

### 3.1 Current MVP Architecture (Single-Tenant Local Mode)
> [!NOTE]
> In accordance with MVP architectural boundaries for local competition evaluation, the system currently operates without multi-user login or token-based authentication. All sessions are logged to local atomic JSON files accessible to the active local user.

### 3.2 Enterprise Multi-User Auth Upgrade Roadmap
To upgrade the system for multi-tenant SaaS deployment, the following authentication architecture will be integrated into the FastAPI backend:
1. **OAuth2 with Password Bearer & JWT:** Implement `FastAPI Security` using `OAuth2PasswordBearer`. Upon login (`POST /api/v1/auth/token`), users receive a cryptographically signed JSON Web Token (JWT) containing their unique user UUID and role scopes.
2. **Dependency-Driven Auth Enforcement:** Create a dependency `get_current_active_user(token: str = Depends(oauth2_scheme))` injected into all `/api/v1/` route handlers.
3. **Database Tenant Isolation:** Migrate `data/history.json` to PostgreSQL. Each networking session record will include a foreign key `user_id`. Queries to `/api/v1/history` will append `WHERE user_id = current_user.id`, guaranteeing strict data privacy across corporate accounts.

---

## 4. Frontend Architecture & Streamlit UI Components

The frontend is built using **Streamlit 1.30+** (`frontend/streamlit_app.py` and `frontend/pages/`), providing an interactive, reactive multi-page web interface.

```
+-----------------------------------------------------------------------------------+
|                        STREAMLIT MULTI-PAGE UI NAVIGATION                         |
+-----------------------------------------------------------------------------------+
|  [Tab 1: Generate Starters]  |  [Tab 2: Fact-Check]      |  [Tab 3: History]      |
|  • Input Desc & Bio          |  • Query Input Box        |  • Search & Filter     |
|  • Display Starter Cards     |  • Wikipedia Summary      |  • Paginated Table     |
|  • 👍/👎 & Star Rating Widgets|  • Confidence Badge       |  • CSV/JSON Export     |
+-----------------------------------------------------------------------------------+
|  [Tab 4: Analytics Dashboard]                                                     |
|  • Total Sessions Metric     • Average Star Rating       • Theme Frequency Charts |
+-----------------------------------------------------------------------------------+
```

### 4.1 Session State Management & Dynamic Key Generation
In Streamlit, every UI widget (buttons, sliders, radio boxes) must possess a globally unique `key` identifier. When rendering lists of generated conversation starters where each starter has its own feedback rating widget and 👍/👎 buttons, static keys cause fatal `DuplicateWidgetID` exceptions.

To solve this, our engineering team implemented **Dynamic Key Generation** linking widget state directly to the backend UUIDv4 `session_id` and the starter array index:

```python
# Conceptual implementation of dynamic key generation in streamlit_app.py
for idx, starter in enumerate(session["starters"]):
    st.markdown(f"**{idx+1}.** {starter}")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        # Unique key prevents widget ID collisions across sessions and starters
        if st.button("👍 Useful", key=f"btn_up_{session['session_id']}_{idx}"):
            submit_feedback(session['session_id'], rating=5, starter_index=idx)
            st.toast("Marked as helpful!")
    with col2:
        if st.button("👎 Needs Work", key=f"btn_down_{session['session_id']}_{idx}"):
            submit_feedback(session['session_id'], rating=2, starter_index=idx)
            st.toast("Feedback recorded.")
```

### 4.2 Streamlit Component Walkthrough
* **Generate Starters Tab (`streamlit_app.py`):** Features text areas for Event Description and User Bio, a slider for `num_starters` (1–10), and an action button. Upon clicking generate, a spinner indicates local CPU inference progress. Results are rendered in clean markdown cards accompanied by interactive star rating widgets.
* **Fact-Check Tab (`streamlit_app.py`):** Provides a clean search box where users can input technical terms or industry buzzwords. The UI displays the Wikipedia extract, a direct markdown hyperlink to the source article, and a color-coded confidence badge (Green for `verified`/`high`, Orange for `unverified`/`low`).
* **History Review Tab (`pages/history.py`):** Connects to `GET /api/v1/history`. Displays a keyword search bar and pagination controls (Previous/Next buttons managing `st.session_state.current_page`). Past sessions are expandable via `st.expander()`. Includes download buttons for CSV and JSON export.
* **Analytics Dashboard Tab (`pages/dashboard.py`):** Connects to `GET /api/v1/history/analytics`. Uses `st.metric()` cards to display Total Sessions and Average Rating. Utilizes native Streamlit bar charts (`st.bar_chart()`) to visualize domain theme frequency distributions and daily usage volume over time.

---

## 5. Configuration Management (`pydantic-settings`)

System configuration is centrally governed by `app/config.py`, which defines a `Settings` class inheriting from `pydantic_settings.BaseSettings`. This ensures that all environment variables are validated at application boot, providing type safety and intelligent default fallbacks.

```python
# Extract from app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Personalized Networking Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins_str: str = "http://localhost:8501,http://127.0.0.1:8501"
    
    data_dir: str = "data"
    history_file: str = "history.json"
    profiles_file: str = "profiles.json"
    
    zero_shot_model: str = "facebook/bart-large-mnli"
    generation_model: str = "gpt2"
    max_new_tokens: int = 80
    num_starters: int = 5
    generation_temperature: float = 0.85
    generation_top_p: float = 0.92
    
    wikipedia_language: str = "en"
    wikipedia_sentences: int = 3
    wikipedia_timeout: int = 10
    max_history_items: int = 1000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 6. Environment Variables Table (`.env.example`)

The repository includes a comprehensive `.env.example` file. Developers copy this file to `.env` to configure local execution:

| Environment Variable | Default Value | Data Type | Description & Purpose |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | Personalized Networking Assistant | String | Display name shown in Swagger UI and Streamlit titles. |
| `APP_VERSION` | 1.0.0 | String | Semantic version tag reported by health and API root endpoints. |
| `DEBUG` | false | Boolean | Toggles detailed debug logging and verbose error reporting. |
| `LOG_LEVEL` | INFO | String | Logging severity threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `HOST` | 0.0.0.0 | String | Network interface binding address for the Uvicorn ASGI server. |
| `PORT` | 8000 | Integer | Listening port for the FastAPI backend service. |
| `ALLOWED_ORIGINS_STR` | http://localhost:8501,... | String | Comma-separated list of CORS origins permitted to call the API. |
| `DATA_DIR` | data | String | Relative or absolute path to the local atomic JSON storage folder. |
| `HISTORY_FILE` | history.json | String | Filename for persisting networking session logs. |
| `PROFILES_FILE` | profiles.json | String | Filename for storing user profile metadata. |
| `ZERO_SHOT_MODEL` | facebook/bart-large-mnli | String | Hugging Face Hub ID for zero-shot NLI theme classification. |
| `GENERATION_MODEL` | gpt2 | String | Hugging Face Hub ID for text generation (124M parameter model). |
| `MAX_NEW_TOKENS` | 80 | Integer | Upper bound on generated tokens per suggestion to control latency. |
| `NUM_STARTERS` | 5 | Integer | Default number of conversation starters generated if unspecified. |
| `GENERATION_TEMPERATURE` | 0.85 | Float | Sampling temperature controlling lexical diversity and creativity. |
| `GENERATION_TOP_P` | 0.92 | Float | Nucleus sampling probability threshold filtering long-tail tokens. |
| `WIKIPEDIA_LANGUAGE` | en | String | Language subdomain code for querying Wikipedia REST API. |
| `WIKIPEDIA_SENTENCES` | 3 | Integer | Number of summary sentences requested from Wikipedia extracts. |
| `WIKIPEDIA_TIMEOUT` | 10 | Integer | Network timeout threshold in seconds for external Wikipedia calls. |
| `MAX_HISTORY_ITEMS` | 1000 | Integer | Maximum number of historical sessions retained in local JSON storage.|

---

## 7. Local Development Workflow & Installation

### 7.1 Installation Prerequisites
* **Operating System:** Windows 10/11, macOS (Intel/M-Series), or Linux (Ubuntu/Debian/CentOS).
* **Python Runtime:** Python 3.9, 3.10, or 3.11 installed and accessible via system PATH.
* **Container Tools (Optional):** Docker Desktop and Docker Compose v2.20+ for containerized execution.

### 7.2 Step-by-Step Developer Workflow (Using `Makefile`)
The repository includes a developer-friendly `Makefile` automating virtual environment creation, dependency installation, linting, testing, and service launch:

```bash
# Step 1: Clone repository & enter project workspace
git clone https://github.com/Personalized-Networking-Assistant/networking-assistant.git
cd networking-assistant

# Step 2: Create local Python virtual environment & install dependencies
make venv
make install

# Step 3: Copy environment configuration template
cp .env.example .env

# Step 4: Execute comprehensive pytest test suite (Verifies all 38 tests pass)
make test

# Step 5: Launch FastAPI backend server in terminal window 1 (Port 8000)
make run-api

# Step 6: Launch Streamlit frontend UI in terminal window 2 (Port 8501)
make run-ui
```

### 7.3 Manual Launch Commands (Without Make)
If operating on Windows PowerShell without `make` installed, execute directly via Python:
```powershell
# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Copy .env
Copy-Item .env.example .env

# Run automated tests
pytest tests/ -v

# Start FastAPI server (in terminal 1)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Streamlit UI (in terminal 2)
streamlit run frontend/streamlit_app.py --server.port 8501
```

---

## 8. Containerized Deployment (Docker & Docker Compose)

To ensure **100% environmental reproducibility** across evaluator machines, the system provides a multi-stage Docker architecture orchestrated via `docker-compose.yml`.

```
+-----------------------------------------------------------------------------------+
|                        DOCKER COMPOSE CONTAINER NETWORK                           |
+-----------------------------------------------------------------------------------+
|  [Container 1: api]                                                               |
|  • Build: Dockerfile (FastAPI Backend)                                            |
|  • Ports: 8000:8000                                                               |
|  • Volumes: ./data:/app/data (Persists JSON history to host disk)                 |
+-----------------------------------------------------------------------------------+
                                         ▲
                                         │ Internal Docker Network (http://api:8000)
                                         ▼
+-----------------------------------------------------------------------------------+
|  [Container 2: frontend]                                                          |
|  • Build: Dockerfile.frontend (Streamlit UI)                                      |
|  • Ports: 8501:8501                                                               |
|  • Environment: BACKEND_URL=http://api:8000/api/v1                                |
|  • Depends On: api (Waits for API container startup)                              |
+-----------------------------------------------------------------------------------+
```

### 8.1 Multi-Stage Containerization Walkthrough
* **Backend Container (`Dockerfile`):** Uses `python:3.10-slim` as a base image. Installs system build dependencies, copies `requirements.txt`, and installs Python wheels. Mounts a volume at `/app/data` to ensure that JSON history files persist on the host machine even if the container is rebuilt or destroyed.
* **Frontend Container (`Dockerfile.frontend`):** Uses `python:3.10-slim`. Installs Streamlit and HTTP client libraries. Configures the environment variable `BACKEND_URL=http://api:8000/api/v1`, allowing the Streamlit container to communicate directly with the backend container over Docker's internal bridged network without routing through localhost.
* **One-Click Orchestration:**
  ```bash
  # Launch both backend and frontend containers in detached mode
  docker-compose up --build -d

  # View real-time container logs
  docker-compose logs -f

  # Stop and remove containers
  docker-compose down
  ```

Once deployed via Docker Compose, access the interactive Streamlit UI at `http://localhost:8501` and the FastAPI Swagger documentation at `http://localhost:8000/docs`.

---

> [!TIP]
> **Next Steps for Evaluators:**  
> Proceed to `Testing.md` to review the comprehensive QA strategy, offline mocking architecture, and the complete Markdown table detailing all 38 pytest unit and integration test cases.

# 🚀 How to Run & Deploy — Personalized Networking Assistant

## Project Location
```
C:\Users\ADMIN\.gemini\antigravity\scratch\networking-assistant\
```

---

## Option 1 — Run Locally (Development)

This is the fastest way to get started. You need **two terminals**.

### Step 1 — Open Terminal, Navigate to Project

```powershell
cd C:\Users\ADMIN\.gemini\antigravity\scratch\networking-assistant
```

### Step 2 — Set Up Virtual Environment (First Time Only)

```powershell
# Create venv (uses Python 3.13)
py -3.13 -m venv venv

# Activate it
venv\Scripts\activate

# Install all packages (~2–3 min first time, downloads torch + transformers)
pip install -r requirements.txt
```

### Step 3 — Configure Environment

```powershell
# Copy the example env file
Copy-Item .env.example .env
```

You can edit `.env` if you want to change settings (defaults work fine out of the box).

### Step 4 — Initialize Data Directory

```powershell
# Create data directory with empty JSON files
New-Item -ItemType Directory -Force -Path data
'[]' | Set-Content data\history.json
'[]' | Set-Content data\profiles.json
```

### Step 5 — Start FastAPI Backend (Terminal 1)

```powershell
# Make sure venv is active
venv\Scripts\activate

# Start the API server (hot-reload enabled)
venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ API is live at: **http://localhost:8000**
📖 Swagger UI: **http://localhost:8000/docs**

> **Note:** First request will download ~1 GB of AI model weights from Hugging Face.
> Subsequent requests use the local cache and are fast.

### Step 6 — Start Streamlit Frontend (Terminal 2)

```powershell
# Open a NEW terminal window, navigate to project
cd C:\Users\ADMIN\.gemini\antigravity\scratch\networking-assistant
venv\Scripts\activate

# Start Streamlit
venv\Scripts\streamlit.exe run frontend/streamlit_app.py --server.port 8501
```

✅ App is live at: **http://localhost:8501**

---

## Option 2 — Run with Docker (Recommended for Production)

Requires **Docker Desktop** installed and running.

### Step 1 — Build and Start

```powershell
cd C:\Users\ADMIN\.gemini\antigravity\scratch\networking-assistant

# Build images and start both services
docker compose up -d
```

### Step 2 — Check Status

```powershell
docker compose ps
docker compose logs -f
```

### Step 3 — Access

| Service | URL |
|---|---|
| Streamlit Frontend | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Swagger Docs | http://localhost:8000/docs |

### Step 4 — Stop

```powershell
docker compose down
```

---

## Option 3 — Cloud Deployment

### Deploy to Railway (Easiest — Free Tier)

1. Push project to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create networking-assistant --public --push
   ```

2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**

3. Railway auto-detects `Dockerfile` — set these environment variables:
   ```
   PORT=8000
   HOST=0.0.0.0
   ```

4. Add a second service for Streamlit with:
   ```
   CMD: streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0
   API_BASE: https://your-backend-url.railway.app/api/v1
   ```

---

### Deploy to Render (Free Tier)

1. Push to GitHub (same as above)
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect repo → Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add a second service for Streamlit

---

### Deploy to Hugging Face Spaces (Easy for ML apps)

1. Create a new **Gradio/Streamlit** Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose **Streamlit** as the SDK
3. Upload your project files
4. Set `API_BASE` env variable to your deployed backend URL

---

## Running Tests

```powershell
cd C:\Users\ADMIN\.gemini\antigravity\scratch\networking-assistant
venv\Scripts\activate

# Run all tests
venv\Scripts\pytest.exe tests/ -v

# With coverage report
venv\Scripts\pytest.exe tests/ -v --cov=app --cov-report=term-missing

# Skip slow tests (no AI model loading)
venv\Scripts\pytest.exe tests/ -v -m "not slow"
```

---

## API Endpoints Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze-event` | Analyze event themes with BART |
| `POST` | `/api/v1/generate-conversation` | Generate starters with GPT-2 |
| `GET` | `/api/v1/fact-check?query=...` | Wikipedia fact-check |
| `GET` | `/api/v1/history` | Paginated session history |
| `GET` | `/api/v1/history/analytics` | Aggregate analytics |
| `GET` | `/api/v1/history/export/json` | Download history as JSON |
| `GET` | `/api/v1/history/export/csv` | Download history as CSV |
| `POST` | `/api/v1/feedback` | Submit star rating & comment |
| `GET` | `/health` | API health + model status |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `uvicorn` not found | Run `venv\Scripts\activate` first |
| Model download slow | First run only — models cache in `~/.cache/huggingface` |
| Port already in use | Kill process: `netstat -ano \| findstr :8000` then `taskkill /PID <id> /F` |
| API shows ❌ Offline in UI | Make sure backend is running on port 8000 first |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the venv |
| Wikipedia returns no results | Check internet connection; Wikipedia API requires outbound HTTPS |

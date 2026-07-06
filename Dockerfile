# ─────────────────────────────────────────────────────────────────────────────
# Personalized Networking Assistant — Dockerfile
# Multi-stage build for a lean production image
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build deps ───────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into a prefix directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-warn-script-location -r requirements.txt

# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="Networking Assistant Team"
LABEL version="1.0.0"
LABEL description="Personalized Networking Assistant - FastAPI + Streamlit"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser frontend/ ./frontend/
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser .env.example ./.env

# Create data directory
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

# Expose ports: 8000 (FastAPI), 8501 (Streamlit)
EXPOSE 8000 8501

# Default: start FastAPI backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

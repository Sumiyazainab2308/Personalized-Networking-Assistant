"""
Test configuration and shared fixtures for pytest.

Provides:
  - FastAPI test client using httpx.AsyncClient
  - Temporary data directory for storage isolation
  - Mocked NLP and generation service fixtures
"""

from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.models.responses import ThemeScore


# ─── Settings Override ────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def temp_data_dir(tmp_path: Path) -> Path:
    """Provide an isolated temporary data directory per test."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture(scope="function")
def test_settings(temp_data_dir: Path) -> Settings:
    """Return Settings instance pointing to the temp data directory."""
    return Settings(
        data_dir=str(temp_data_dir),
        history_file="history.json",
        profiles_file="profiles.json",
        debug=True,
        log_level="WARNING",
    )


@pytest.fixture(autouse=True)
def override_settings(test_settings: Settings, monkeypatch) -> None:
    """
    Auto-apply settings override for every test function.

    Patches get_settings in every module that calls it so all storage
    operations use the isolated temp directory.
    """
    monkeypatch.setattr("app.config.get_settings", lambda: test_settings)
    monkeypatch.setattr("app.services.storage_service.get_settings", lambda: test_settings)
    monkeypatch.setattr("app.services.nlp_service.get_settings", lambda: test_settings)
    monkeypatch.setattr("app.services.generation_service.get_settings", lambda: test_settings)
    monkeypatch.setattr("app.services.factcheck_service.get_settings", lambda: test_settings)


# ─── FastAPI Test Client ──────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def async_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# ─── Sample Data ──────────────────────────────────────────────────────────────
@pytest.fixture
def sample_event_description() -> str:
    return (
        "NeurIPS 2024 — A premier machine learning conference bringing together "
        "researchers and practitioners in deep learning, NLP, and reinforcement learning."
    )


@pytest.fixture
def sample_user_bio() -> str:
    return "Senior ML Engineer specializing in NLP and large-scale model training."


@pytest.fixture
def sample_themes() -> list:
    return ["technology", "science", "education"]


@pytest.fixture
def sample_theme_scores() -> list:
    return [
        ThemeScore(label="technology", score=0.92),
        ThemeScore(label="science", score=0.85),
        ThemeScore(label="education", score=0.71),
        ThemeScore(label="business", score=0.45),
    ]


@pytest.fixture
def sample_starters() -> list:
    return [
        "What projects are you currently working on in machine learning?",
        "How did you first get involved in deep learning research?",
        "What NLP trends are you most excited about right now?",
        "What has been your biggest challenge in NLP this year?",
        "Are there any frameworks you would recommend for NLP tasks?",
    ]


@pytest.fixture
def sample_session_record() -> dict:
    return {
        "session_id": "test-session-001",
        "event_description": "A technology networking event focused on AI.",
        "user_bio": "Senior ML Engineer.",
        "themes": ["technology", "science"],
        "starters": ["What projects are you working on?"],
        "timestamp": "2024-01-15T10:00:00",
        "feedback_rating": None,
        "feedback_comment": None,
    }


# ─── NLP / Generation Mocks ───────────────────────────────────────────────────
@pytest.fixture
def mock_classify_event(sample_theme_scores):
    """Mock nlp_service.classify_event to return sample theme scores."""
    with patch(
        "app.services.nlp_service.classify_event",
        return_value=sample_theme_scores,
    ) as mock:
        yield mock


@pytest.fixture
def mock_generate_starters(sample_starters):
    """Mock generation_service.generate_starters to return sample starters."""
    with patch(
        "app.services.generation_service.generate_starters",
        return_value=sample_starters,
    ) as mock:
        yield mock


@pytest.fixture
def mock_fact_check():
    """Mock factcheck_service.fact_check_multiple to return Wikipedia results."""
    from app.models.responses import FactCheckResult

    results = [
        FactCheckResult(
            query="artificial intelligence",
            found=True,
            summary="Artificial intelligence (AI) is intelligence demonstrated by machines.",
            url="https://en.wikipedia.org/wiki/Artificial_intelligence",
            confidence="verified",
        )
    ]
    with patch(
        "app.services.factcheck_service.fact_check_multiple",
        return_value=results,
    ) as mock:
        yield mock

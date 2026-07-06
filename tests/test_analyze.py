"""
Tests for POST /api/v1/analyze-event endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_event_success(
    async_client: AsyncClient,
    mock_classify_event,
    sample_event_description: str,
    sample_user_bio: str,
) -> None:
    """Valid request returns 200 with theme scores and session_id."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={
            "event_description": sample_event_description,
            "user_bio": sample_user_bio,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0
    assert "themes" in data
    assert len(data["themes"]) > 0
    assert "top_theme" in data
    assert data["top_theme"] == "technology"
    assert data["event_description"] == sample_event_description
    mock_classify_event.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_event_without_bio(
    async_client: AsyncClient,
    mock_classify_event,
    sample_event_description: str,
) -> None:
    """Request without user_bio is valid and returns 200."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"event_description": sample_event_description},
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data


@pytest.mark.asyncio
async def test_analyze_event_short_description(
    async_client: AsyncClient,
) -> None:
    """Event description shorter than 10 chars returns 422."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"event_description": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_event_blank_description(
    async_client: AsyncClient,
) -> None:
    """Blank (whitespace-only) event description returns 422."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"event_description": "          "},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_event_missing_description(
    async_client: AsyncClient,
) -> None:
    """Missing required event_description field returns 422."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"user_bio": "Some bio"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_event_too_long_description(
    async_client: AsyncClient,
) -> None:
    """Event description exceeding 2000 chars returns 422."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"event_description": "a" * 2001},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_event_response_has_timestamp(
    async_client: AsyncClient,
    mock_classify_event,
    sample_event_description: str,
) -> None:
    """Response includes a valid ISO timestamp."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"event_description": sample_event_description},
    )
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "T" in data["timestamp"]  # ISO format check


@pytest.mark.asyncio
async def test_analyze_event_theme_scores_sorted(
    async_client: AsyncClient,
    mock_classify_event,
    sample_event_description: str,
) -> None:
    """Returned themes should include label and score fields."""
    response = await async_client.post(
        "/api/v1/analyze-event",
        json={"event_description": sample_event_description},
    )
    assert response.status_code == 200
    themes = response.json()["themes"]
    for theme in themes:
        assert "label" in theme
        assert "score" in theme
        assert 0.0 <= theme["score"] <= 1.0

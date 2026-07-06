"""
Tests for GET /api/v1/history and related history endpoints.
"""

import json

import pytest
from httpx import AsyncClient

from app.services import storage_service


@pytest.mark.asyncio
async def test_history_empty_initially(async_client: AsyncClient) -> None:
    """History starts empty."""
    response = await async_client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_history_returns_saved_session(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """A saved session should appear in history."""
    storage_service.save_session(sample_session_record)

    response = await async_client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["session_id"] == sample_session_record["session_id"]


@pytest.mark.asyncio
async def test_history_pagination(
    async_client: AsyncClient,
) -> None:
    """Pagination parameters work correctly."""
    # Insert 15 sessions
    for i in range(15):
        storage_service.save_session(
            {
                "session_id": f"session-{i:03d}",
                "event_description": f"Event number {i} about technology and AI.",
                "themes": ["technology"],
                "starters": [],
                "timestamp": f"2024-01-{i+1:02d}T10:00:00",
            }
        )

    # Page 1 with page_size=5
    resp_p1 = await async_client.get(
        "/api/v1/history", params={"page": 1, "page_size": 5}
    )
    assert resp_p1.status_code == 200
    d1 = resp_p1.json()
    assert len(d1["items"]) == 5
    assert d1["total"] == 15
    assert d1["page"] == 1

    # Page 2
    resp_p2 = await async_client.get(
        "/api/v1/history", params={"page": 2, "page_size": 5}
    )
    assert resp_p2.status_code == 200
    d2 = resp_p2.json()
    assert len(d2["items"]) == 5
    assert d2["page"] == 2

    # No overlap
    ids_p1 = {item["session_id"] for item in d1["items"]}
    ids_p2 = {item["session_id"] for item in d2["items"]}
    assert ids_p1.isdisjoint(ids_p2)


@pytest.mark.asyncio
async def test_history_search(
    async_client: AsyncClient,
) -> None:
    """Search filter returns only matching sessions."""
    storage_service.save_session(
        {
            "session_id": "tech-session",
            "event_description": "Technology and AI conference.",
            "themes": ["technology"],
            "starters": [],
            "timestamp": "2024-01-01T10:00:00",
        }
    )
    storage_service.save_session(
        {
            "session_id": "health-session",
            "event_description": "Healthcare innovation summit.",
            "themes": ["healthcare"],
            "starters": [],
            "timestamp": "2024-01-02T10:00:00",
        }
    )

    resp = await async_client.get("/api/v1/history", params={"search": "healthcare"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["session_id"] == "health-session"


@pytest.mark.asyncio
async def test_history_analytics(
    async_client: AsyncClient,
) -> None:
    """Analytics endpoint returns expected keys."""
    storage_service.save_session(
        {
            "session_id": "analytics-test",
            "event_description": "Analytics test event about technology.",
            "themes": ["technology", "business"],
            "starters": [],
            "timestamp": "2024-01-10T10:00:00",
            "feedback_rating": 4,
        }
    )

    resp = await async_client.get("/api/v1/history/analytics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_sessions" in data
    assert "avg_rating" in data
    assert "theme_counts" in data
    assert "sessions_per_day" in data
    assert data["total_sessions"] == 1
    assert data["avg_rating"] == 4.0
    assert "technology" in data["theme_counts"]


@pytest.mark.asyncio
async def test_history_export_json(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """JSON export returns valid JSON content."""
    storage_service.save_session(sample_session_record)
    resp = await async_client.get("/api/v1/history/export/json")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    data = json.loads(resp.content)
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_history_export_csv(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """CSV export returns text/csv content."""
    storage_service.save_session(sample_session_record)
    resp = await async_client.get("/api/v1/history/export/csv")
    assert resp.status_code == 200
    assert "csv" in resp.headers["content-type"]
    content = resp.content.decode("utf-8")
    assert "session_id" in content  # header row
    assert sample_session_record["session_id"] in content


@pytest.mark.asyncio
async def test_history_page_too_large(async_client: AsyncClient) -> None:
    """page_size > 100 returns 422."""
    resp = await async_client.get("/api/v1/history", params={"page_size": 200})
    assert resp.status_code == 422

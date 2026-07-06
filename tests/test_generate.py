"""
Tests for POST /api/v1/generate-conversation endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_conversation_success(
    async_client: AsyncClient,
    mock_classify_event,
    mock_generate_starters,
    sample_event_description: str,
    sample_user_bio: str,
) -> None:
    """Valid request returns 200 with starters list."""
    response = await async_client.post(
        "/api/v1/generate-conversation",
        json={
            "event_description": sample_event_description,
            "user_bio": sample_user_bio,
            "num_starters": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "starters" in data
    assert isinstance(data["starters"], list)
    assert len(data["starters"]) > 0
    assert "themes_used" in data
    assert isinstance(data["themes_used"], list)
    mock_generate_starters.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_precomputed_themes(
    async_client: AsyncClient,
    mock_generate_starters,
    sample_event_description: str,
    sample_themes: list,
) -> None:
    """Supplying pre-computed themes should skip classification."""
    response = await async_client.post(
        "/api/v1/generate-conversation",
        json={
            "event_description": sample_event_description,
            "themes": sample_themes,
            "num_starters": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["themes_used"] == sample_themes
    # generate_starters should still be called
    mock_generate_starters.assert_called_once()


@pytest.mark.asyncio
async def test_generate_num_starters_range(
    async_client: AsyncClient,
    mock_classify_event,
    mock_generate_starters,
    sample_event_description: str,
) -> None:
    """num_starters must be between 1 and 10."""
    # Valid boundary values
    for n in [1, 5, 10]:
        response = await async_client.post(
            "/api/v1/generate-conversation",
            json={"event_description": sample_event_description, "num_starters": n},
        )
        assert response.status_code == 200, f"Expected 200 for num_starters={n}"

    # Invalid values
    for n in [0, 11, -1, 100]:
        response = await async_client.post(
            "/api/v1/generate-conversation",
            json={"event_description": sample_event_description, "num_starters": n},
        )
        assert response.status_code == 422, f"Expected 422 for num_starters={n}"


@pytest.mark.asyncio
async def test_generate_short_description(async_client: AsyncClient) -> None:
    """Too-short event description returns 422."""
    response = await async_client.post(
        "/api/v1/generate-conversation",
        json={"event_description": "hi"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_response_includes_metadata(
    async_client: AsyncClient,
    mock_classify_event,
    mock_generate_starters,
    sample_event_description: str,
    sample_user_bio: str,
) -> None:
    """Response includes session_id, timestamp, event_description, user_bio."""
    response = await async_client.post(
        "/api/v1/generate-conversation",
        json={
            "event_description": sample_event_description,
            "user_bio": sample_user_bio,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event_description"] == sample_event_description
    assert data["user_bio"] == sample_user_bio
    assert "timestamp" in data
    assert "session_id" in data


@pytest.mark.asyncio
async def test_generate_persists_session(
    async_client: AsyncClient,
    mock_classify_event,
    mock_generate_starters,
    sample_event_description: str,
) -> None:
    """Generated session should appear in history."""
    gen_resp = await async_client.post(
        "/api/v1/generate-conversation",
        json={"event_description": sample_event_description},
    )
    assert gen_resp.status_code == 200
    session_id = gen_resp.json()["session_id"]

    hist_resp = await async_client.get("/api/v1/history")
    assert hist_resp.status_code == 200
    session_ids = [item["session_id"] for item in hist_resp.json()["items"]]
    assert session_id in session_ids

"""
Tests for POST /api/v1/feedback endpoint.
"""

import pytest
from httpx import AsyncClient

from app.services import storage_service


@pytest.mark.asyncio
async def test_feedback_success(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """Valid feedback submission returns 200."""
    storage_service.save_session(sample_session_record)

    response = await async_client.post(
        "/api/v1/feedback",
        json={
            "session_id": sample_session_record["session_id"],
            "rating": 5,
            "comment": "Great conversation starters!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == sample_session_record["session_id"]
    assert data["rating"] == 5
    assert "message" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_feedback_persists_rating(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """Feedback rating is persisted to the session record."""
    storage_service.save_session(sample_session_record)

    await async_client.post(
        "/api/v1/feedback",
        json={
            "session_id": sample_session_record["session_id"],
            "rating": 3,
            "comment": "Could be better.",
        },
    )

    # Check via storage directly
    session = storage_service.get_session(sample_session_record["session_id"])
    assert session is not None
    assert session["feedback_rating"] == 3
    assert session["feedback_comment"] == "Could be better."


@pytest.mark.asyncio
async def test_feedback_rating_boundary_values(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """Ratings 1 through 5 are all accepted."""
    storage_service.save_session(sample_session_record)

    for rating in [1, 2, 3, 4, 5]:
        response = await async_client.post(
            "/api/v1/feedback",
            json={
                "session_id": sample_session_record["session_id"],
                "rating": rating,
            },
        )
        assert response.status_code == 200, f"Failed for rating={rating}"


@pytest.mark.asyncio
async def test_feedback_invalid_rating_low(async_client: AsyncClient) -> None:
    """Rating below 1 returns 422."""
    response = await async_client.post(
        "/api/v1/feedback",
        json={"session_id": "any-session", "rating": 0},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_feedback_invalid_rating_high(async_client: AsyncClient) -> None:
    """Rating above 5 returns 422."""
    response = await async_client.post(
        "/api/v1/feedback",
        json={"session_id": "any-session", "rating": 6},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_feedback_missing_session_id(async_client: AsyncClient) -> None:
    """Missing session_id returns 422."""
    response = await async_client.post(
        "/api/v1/feedback",
        json={"rating": 4},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_feedback_missing_rating(async_client: AsyncClient) -> None:
    """Missing rating returns 422."""
    response = await async_client.post(
        "/api/v1/feedback",
        json={"session_id": "some-session"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_feedback_without_comment(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """Feedback without comment is valid."""
    storage_service.save_session(sample_session_record)
    response = await async_client.post(
        "/api/v1/feedback",
        json={
            "session_id": sample_session_record["session_id"],
            "rating": 4,
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_feedback_with_starter_index(
    async_client: AsyncClient,
    sample_session_record: dict,
) -> None:
    """Feedback with starter_index is accepted."""
    storage_service.save_session(sample_session_record)
    response = await async_client.post(
        "/api/v1/feedback",
        json={
            "session_id": sample_session_record["session_id"],
            "rating": 5,
            "starter_index": 2,
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_feedback_unknown_session(async_client: AsyncClient) -> None:
    """Feedback for unknown session_id still returns 200 (async tolerance)."""
    response = await async_client.post(
        "/api/v1/feedback",
        json={"session_id": "nonexistent-session-xyz", "rating": 3},
    )
    # Accepted to support out-of-order / async feedback submission
    assert response.status_code == 200

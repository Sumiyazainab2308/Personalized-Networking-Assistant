"""
Tests for GET /api/v1/fact-check endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_fact_check_single_query(
    async_client: AsyncClient,
    mock_fact_check,
) -> None:
    """Single valid query returns 200 with results."""
    response = await async_client.get(
        "/api/v1/fact-check",
        params={"query": "artificial intelligence"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    result = data["results"][0]
    assert result["query"] == "artificial intelligence"
    assert result["found"] is True
    assert result["confidence"] == "verified"
    assert "summary" in result
    assert "url" in result


@pytest.mark.asyncio
async def test_fact_check_multiple_queries(
    async_client: AsyncClient,
    mock_fact_check,
) -> None:
    """Multiple query params are accepted."""
    response = await async_client.get(
        "/api/v1/fact-check",
        params=[
            ("query", "artificial intelligence"),
            ("query", "machine learning"),
        ],
    )
    assert response.status_code == 200
    data = response.json()
    # Mock returns one result regardless; verify structure
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_fact_check_missing_query(async_client: AsyncClient) -> None:
    """Request without query parameter returns 422."""
    response = await async_client.get("/api/v1/fact-check")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_fact_check_result_structure(
    async_client: AsyncClient,
    mock_fact_check,
) -> None:
    """Each result should have required fields."""
    response = await async_client.get(
        "/api/v1/fact-check",
        params={"query": "artificial intelligence"},
    )
    assert response.status_code == 200
    for result in response.json()["results"]:
        assert "query" in result
        assert "found" in result
        assert "confidence" in result
        # summary and url may be None if not found


@pytest.mark.asyncio
async def test_fact_check_response_has_timestamp(
    async_client: AsyncClient,
    mock_fact_check,
) -> None:
    """Response includes a timestamp field."""
    response = await async_client.get(
        "/api/v1/fact-check",
        params={"query": "machine learning"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_fact_check_deduplication(
    async_client: AsyncClient,
    mock_fact_check,
) -> None:
    """Duplicate query values are deduplicated before processing."""
    response = await async_client.get(
        "/api/v1/fact-check",
        params=[
            ("query", "artificial intelligence"),
            ("query", "artificial intelligence"),  # duplicate
        ],
    )
    assert response.status_code == 200
    # Mock is called once with deduplicated list
    args = mock_fact_check.call_args[0][0]
    assert args.count("artificial intelligence") == 1

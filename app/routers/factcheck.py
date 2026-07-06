"""
Router: GET /fact-check

Fact-checks one or more queries against Wikipedia and returns
summaries, URLs, and confidence levels.
"""

from typing import Annotated, List

from fastapi import APIRouter, Query

from app.models.responses import FactCheckResponse
from app.services.orchestrator import orchestrate_fact_check
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/fact-check", tags=["Fact Check"])


@router.get(
    "",
    response_model=FactCheckResponse,
    summary="Fact-Check Topics via Wikipedia",
    description=(
        "Verify one or more topics or claims by querying the Wikipedia API. "
        "Pass multiple 'query' parameters to batch-check multiple topics. "
        "Returns summaries, Wikipedia URLs, and confidence levels."
    ),
    responses={
        200: {"description": "Fact-check results"},
        422: {"description": "Invalid query parameters"},
        502: {"description": "Wikipedia API error"},
    },
)
async def fact_check(
    query: Annotated[
        List[str],
        Query(
            description="Topic or claim to fact-check. Repeat for multiple queries.",
        ),
    ],
) -> FactCheckResponse:
    """
    Fact-check one or more topics via Wikipedia.

    Args:
        query: One or more topic strings to look up.

    Returns:
        FactCheckResponse: List of fact-check results.
    """
    # Deduplicate while preserving order
    seen: set = set()
    unique_queries: List[str] = []
    for q in query:
        q_stripped = q.strip()
        # Skip empty or very short queries
        if len(q_stripped) >= 2 and q_stripped not in seen:
            seen.add(q_stripped)
            unique_queries.append(q_stripped)

    if not unique_queries:
        from fastapi import HTTPException  # noqa: PLC0415
        raise HTTPException(
            status_code=422,
            detail="At least one non-empty query (min 2 characters) is required.",
        )

    logger.info("GET /fact-check | %d unique queries", len(unique_queries))
    return orchestrate_fact_check(unique_queries)

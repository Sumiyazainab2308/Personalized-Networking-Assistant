"""
Router: GET /history

Returns paginated interaction history with optional search filtering.
Also exposes GET /history/analytics and GET /history/export endpoints.
"""

import csv
import io
import json
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import Response, StreamingResponse

from app.models.responses import HistoryResponse
from app.services import storage_service
from app.services.orchestrator import orchestrate_get_history
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "",
    response_model=HistoryResponse,
    summary="Get Interaction History",
    description=(
        "Retrieve paginated interaction history. Supports optional search "
        "filtering by event description or themes."
    ),
)
async def get_history(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Items per page (max 100)."
    ),
    search: Optional[str] = Query(
        default=None, description="Filter by event description or theme keywords."
    ),
) -> HistoryResponse:
    """
    Retrieve paginated history with optional search.

    Args:
        page: Page number.
        page_size: Items per page.
        search: Optional text filter.

    Returns:
        HistoryResponse: Paginated list of session records.
    """
    logger.info(
        "GET /history | page=%d, page_size=%d, search=%s", page, page_size, search
    )
    return orchestrate_get_history(page=page, page_size=page_size, search=search)


@router.get(
    "/analytics",
    summary="Get History Analytics",
    description="Returns aggregate analytics: theme counts, avg rating, sessions per day.",
)
async def get_analytics() -> dict:
    """
    Return analytics summary of session history.

    Returns:
        dict: Analytics data including theme distribution and rating averages.
    """
    logger.info("GET /history/analytics")
    return storage_service.get_analytics()


@router.get(
    "/export/json",
    summary="Export History as JSON",
    description="Download the full interaction history as a JSON file.",
    response_class=Response,
)
async def export_json() -> Response:
    """
    Export all history records as a downloadable JSON file.

    Returns:
        Response: JSON file download.
    """
    logger.info("GET /history/export/json")
    raw = storage_service.get_history(page=1, page_size=10000)
    content = json.dumps(raw["items"], ensure_ascii=False, indent=2, default=str)
    return Response(
        content=content.encode("utf-8"),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=networking_history.json"},
    )


@router.get(
    "/export/csv",
    summary="Export History as CSV",
    description="Download the full interaction history as a CSV file.",
)
async def export_csv() -> StreamingResponse:
    """
    Export all history records as a downloadable CSV file.

    Returns:
        StreamingResponse: CSV file download.
    """
    logger.info("GET /history/export/csv")
    raw = storage_service.get_history(page=1, page_size=10000)

    output = io.StringIO()
    fieldnames = [
        "session_id",
        "timestamp",
        "event_description",
        "user_bio",
        "themes",
        "starters",
        "feedback_rating",
        "feedback_comment",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for item in raw["items"]:
        item["themes"] = ", ".join(item.get("themes", []))
        item["starters"] = " | ".join(item.get("starters", []))
        writer.writerow(item)

    output.seek(0)
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=networking_history.csv"
        },
    )

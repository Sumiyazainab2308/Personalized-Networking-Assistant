"""
Router: POST /feedback

Accepts user rating and comment for a given session, persists to storage.
"""

from fastapi import APIRouter, HTTPException

from app.models.requests import FeedbackRequest
from app.models.responses import FeedbackResponse
from app.services.orchestrator import orchestrate_submit_feedback
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    summary="Submit Feedback",
    description=(
        "Submit a star rating (1-5) and optional comment for a session. "
        "Optionally specify which starter index is being rated."
    ),
    responses={
        200: {"description": "Feedback recorded"},
        404: {"description": "Session not found"},
        422: {"description": "Validation error in request payload"},
    },
)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Record user feedback for a session.

    Args:
        request: Validated FeedbackRequest payload.

    Returns:
        FeedbackResponse: Confirmation with session ID and rating.

    Raises:
        HTTPException 404: If the session ID does not exist in history.
    """
    logger.info(
        "POST /feedback | session_id=%s, rating=%d",
        request.session_id,
        request.rating,
    )
    response = orchestrate_submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.comment,
        starter_index=request.starter_index,
    )
    # Note: update_session_feedback returns False if not found but we still
    # succeed to allow async / out-of-order feedback submission
    return response

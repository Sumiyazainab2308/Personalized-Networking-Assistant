"""
Router: POST /analyze-event

Accepts event description + optional user bio, runs zero-shot
classification, returns theme scores and session ID.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.requests import AnalyzeEventRequest
from app.models.responses import AnalyzeEventResponse
from app.services.orchestrator import orchestrate_analyze_event
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyze-event", tags=["Analysis"])


@router.post(
    "",
    response_model=AnalyzeEventResponse,
    summary="Analyze Networking Event",
    description=(
        "Submit an event description to classify it into thematic categories "
        "using zero-shot classification (BART/DistilBERT). Returns a ranked "
        "list of themes and a session ID for subsequent requests."
    ),
    responses={
        200: {"description": "Successful event analysis"},
        422: {"description": "Validation error in request payload"},
        500: {"description": "Internal NLP service error"},
        503: {"description": "Model not yet loaded or unavailable"},
    },
)
async def analyze_event(request: AnalyzeEventRequest) -> AnalyzeEventResponse:
    """
    Classify a networking event description into thematic categories.

    Args:
        request: Validated AnalyzeEventRequest payload.

    Returns:
        AnalyzeEventResponse: Classification results with session ID and themes.
    """
    logger.info(
        "POST /analyze-event | event_length=%d", len(request.event_description)
    )
    return orchestrate_analyze_event(
        event_description=request.event_description,
        user_bio=request.user_bio,
    )

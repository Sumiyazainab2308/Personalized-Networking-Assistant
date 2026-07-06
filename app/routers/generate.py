"""
Router: POST /generate-conversation

Generates personalized conversation starters using GPT-2 based on
event themes (optionally from a prior analysis session).
"""

from fastapi import APIRouter

from app.models.requests import GenerateConversationRequest
from app.models.responses import ConversationStarterResponse
from app.services.orchestrator import orchestrate_generate_conversation
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/generate-conversation", tags=["Generation"])


@router.post(
    "",
    response_model=ConversationStarterResponse,
    summary="Generate Conversation Starters",
    description=(
        "Generate personalized networking conversation starters using "
        "GPT-2 Small. Optionally supply pre-classified themes to skip "
        "the classification step. Returns a list of ready-to-use starters."
    ),
    responses={
        200: {"description": "Successful generation"},
        422: {"description": "Validation error in request payload"},
        500: {"description": "Generation or NLP error"},
        503: {"description": "Model not yet loaded"},
    },
)
async def generate_conversation(
    request: GenerateConversationRequest,
) -> ConversationStarterResponse:
    """
    Generate conversation starters for a networking event.

    Args:
        request: Validated GenerateConversationRequest payload.

    Returns:
        ConversationStarterResponse: Generated starters with metadata.
    """
    logger.info(
        "POST /generate-conversation | num_starters=%d", request.num_starters
    )
    return orchestrate_generate_conversation(
        event_description=request.event_description,
        user_bio=request.user_bio,
        themes=request.themes,
        num_starters=request.num_starters,
    )

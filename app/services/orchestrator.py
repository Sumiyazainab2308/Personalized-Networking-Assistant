"""
Orchestrator — Central coordination layer between API routes and services.

This module handles the sequence of operations required for each use case,
including error handling, logging, and persistence. It keeps individual
services focused on their own concerns (SRP) while coordinating them here.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.responses import (
    AnalyzeEventResponse,
    ConversationStarterResponse,
    FactCheckResponse,
    FeedbackResponse,
    HistoryItem,
    HistoryResponse,
    ThemeScore,
)
from app.services import (
    factcheck_service,
    generation_service,
    nlp_service,
    storage_service,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware, Python 3.11+ compatible)."""
    return datetime.now(tz=timezone.utc)


def orchestrate_analyze_event(
    event_description: str,
    user_bio: Optional[str] = None,
) -> AnalyzeEventResponse:
    """
    Orchestrate the full event analysis flow.

    Steps:
      1. Classify event description using NLP service (DistilBERT/BART).
      2. Persist session record to storage.
      3. Return structured response.

    Args:
        event_description: Plain-text event description.
        user_bio: Optional user bio.

    Returns:
        AnalyzeEventResponse: Analysis results with themes and session ID.
    """
    session_id = str(uuid.uuid4())
    logger.info("Starting event analysis. session_id=%s", session_id)

    theme_scores: List[ThemeScore] = nlp_service.classify_event(event_description)
    top_themes = nlp_service.get_top_themes(theme_scores)

    # Persist session
    storage_service.save_session(
        {
            "session_id": session_id,
            "event_description": event_description,
            "user_bio": user_bio,
            "themes": [ts.label for ts in theme_scores[:5]],
            "starters": [],
            "timestamp": _utcnow().isoformat(),
        }
    )

    logger.info(
        "Event analyzed. session_id=%s, top_theme=%s",
        session_id,
        theme_scores[0].label if theme_scores else "unknown",
    )

    return AnalyzeEventResponse(
        session_id=session_id,
        event_description=event_description,
        themes=theme_scores,
        top_theme=theme_scores[0].label if theme_scores else "unknown",
        timestamp=_utcnow(),
    )


def orchestrate_generate_conversation(
    event_description: str,
    user_bio: Optional[str] = None,
    themes: Optional[List[str]] = None,
    num_starters: int = 5,
) -> ConversationStarterResponse:
    """
    Orchestrate conversation starter generation.

    Steps:
      1. Classify event if themes not provided.
      2. Generate starters with GPT-2.
      3. Persist session.
      4. Return structured response.

    Args:
        event_description: Plain-text event description.
        user_bio: Optional user bio for personalization.
        themes: Pre-classified themes (skips classification if provided).
        num_starters: Number of starters to generate.

    Returns:
        ConversationStarterResponse: Generated starters and metadata.
    """
    session_id = str(uuid.uuid4())
    logger.info("Starting conversation generation. session_id=%s", session_id)

    # Step 1: classify (or use provided themes)
    if themes:
        themes_used = themes
        logger.debug("Using pre-provided themes: %s", themes_used)
    else:
        theme_scores = nlp_service.classify_event(event_description)
        themes_used = nlp_service.get_top_themes(theme_scores)
        logger.debug("Classified themes: %s", themes_used)

    # Step 2: generate starters
    starters = generation_service.generate_starters(
        themes=themes_used,
        event_description=event_description,
        user_bio=user_bio,
        num_starters=num_starters,
    )

    # Step 3: persist
    storage_service.save_session(
        {
            "session_id": session_id,
            "event_description": event_description,
            "user_bio": user_bio,
            "themes": themes_used,
            "starters": starters,
            "timestamp": _utcnow().isoformat(),
        }
    )

    logger.info(
        "Generated %d starters. session_id=%s", len(starters), session_id
    )

    return ConversationStarterResponse(
        session_id=session_id,
        starters=starters,
        themes_used=themes_used,
        event_description=event_description,
        user_bio=user_bio,
        timestamp=_utcnow(),
    )


def orchestrate_fact_check(queries: List[str]) -> FactCheckResponse:
    """
    Orchestrate fact-checking of one or more queries.

    Args:
        queries: List of topics or claims to verify.

    Returns:
        FactCheckResponse: Results for all queries.
    """
    logger.info("Fact-checking %d queries.", len(queries))
    results = factcheck_service.fact_check_multiple(queries)
    return FactCheckResponse(results=results, timestamp=_utcnow())


def orchestrate_get_history(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
) -> HistoryResponse:
    """
    Orchestrate retrieval of paginated history.

    Args:
        page: Page number.
        page_size: Items per page.
        search: Optional filter term.

    Returns:
        HistoryResponse: Paginated history records.
    """
    raw = storage_service.get_history(page=page, page_size=page_size, search=search)
    items: List[HistoryItem] = []

    for record in raw["items"]:
        try:
            ts_str = record.get("timestamp", _utcnow().isoformat())
            # Handle both naive and aware ISO strings
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            items.append(
                HistoryItem(
                    session_id=record.get("session_id", ""),
                    event_description=record.get("event_description", ""),
                    user_bio=record.get("user_bio"),
                    themes=record.get("themes", []),
                    starters=record.get("starters", []),
                    feedback_rating=record.get("feedback_rating"),
                    feedback_comment=record.get("feedback_comment"),
                    timestamp=ts,
                    fact_checks=record.get("fact_checks", []),
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping malformed history record: %s", exc)

    return HistoryResponse(
        items=items,
        total=raw["total"],
        page=raw["page"],
        page_size=raw["page_size"],
    )


def orchestrate_submit_feedback(
    session_id: str,
    rating: int,
    comment: Optional[str] = None,
    starter_index: Optional[int] = None,
) -> FeedbackResponse:
    """
    Orchestrate user feedback submission.

    Args:
        session_id: Session to attach feedback to.
        rating: 1–5 star rating.
        comment: Optional text comment.
        starter_index: Optional index of the rated starter.

    Returns:
        FeedbackResponse: Confirmation of saved feedback.
    """
    logger.info("Saving feedback. session_id=%s, rating=%d", session_id, rating)

    storage_service.update_session_feedback(
        session_id=session_id,
        rating=rating,
        comment=comment,
        starter_index=starter_index,
    )

    return FeedbackResponse(
        session_id=session_id,
        message="Feedback recorded successfully.",
        rating=rating,
        timestamp=_utcnow(),
    )

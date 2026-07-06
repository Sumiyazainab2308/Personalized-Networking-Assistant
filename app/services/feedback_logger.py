"""
Feedback Logger Service — SmartBridge-compatible module alias.

This module captures explicit user feedback on individual conversation starters
as described in the SmartBridge project specification (Epic 2: Core
Functionalities Development).

Feedback data forms the foundation for a future recommendation improvement loop.
Each feedback entry captures:
  - The exact suggestion text that was rated (to correlate with generated content)
  - The action taken ('like' or 'dislike', shown as 👍 / 👎 in the UI)
  - A timestamp

This structured format enables analytics — identifying which types of suggestions
consistently receive positive feedback, potentially informing prompt engineering
improvements.

Usage:
    from app.services.feedback_logger import log_feedback, load_feedback

    log_feedback(
        suggestion="What's your view on AI in healthcare?",
        action="like",
        session_id="abc-123"
    )

    feedback_history = load_feedback()  # Returns list of all feedback
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Feedback is stored alongside history in data/feedback.json
FEEDBACK_FILE = "feedback.json"


def _get_feedback_path() -> Path:
    """Return the path to the feedback JSON file."""
    settings = get_settings()
    return Path(settings.data_dir) / FEEDBACK_FILE


def log_feedback(
    suggestion: str,
    action: str,
    session_id: Optional[str] = None,
    rating: Optional[int] = None,
    comment: Optional[str] = None,
) -> None:
    """
    Append a user feedback entry to the persistent feedback file.

    Each entry captures the suggestion text, user action, and timestamp.
    The read-modify-write pattern is used for data integrity.

    Args:
        suggestion: The exact conversation starter text that was rated.
            This allows correlation between feedback and specific generated content.
        action: User action — either 'like' (👍) or 'dislike' (👎).
            Used as-is for display in the Feedback History View.
        session_id: Optional session ID to link feedback to a specific conversation.
        rating: Optional numeric rating (1–5 stars) in addition to like/dislike.
        comment: Optional free-text comment from the user.

    Example::

        log_feedback(
            suggestion="What brought you to explore blockchain for clinical data?",
            action="like",
            session_id="session-uuid-here"
        )
    """
    feedback_path = _get_feedback_path()

    # Ensure data directory exists
    feedback_path.parent.mkdir(parents=True, exist_ok=True)

    entry: Dict[str, Any] = {
        "suggestion": suggestion,
        "action": action,  # 'like' or 'dislike'
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
    if session_id:
        entry["session_id"] = session_id
    if rating is not None:
        entry["rating"] = rating
    if comment:
        entry["comment"] = comment

    # Read-modify-write pattern (consistent with history_logger)
    existing: List[Dict] = []
    if feedback_path.exists():
        try:
            with open(feedback_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    existing.append(entry)

    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    logger.info(
        "log_feedback | action=%s | session=%s",
        action,
        session_id or "unknown",
    )


def load_feedback(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Read and return recent feedback entries.

    Always returns a list — even when no feedback has been saved yet.
    Entries are returned in reverse chronological order (newest first).

    Args:
        limit: Maximum number of feedback entries to return.
            Defaults to 10 (as specified in SmartBridge UI spec:
            "up to 10 recent feedback entries").

    Returns:
        List[Dict]: List of feedback dictionaries in reverse chronological order.
            Each dict contains at minimum:
            - ``suggestion`` (str): The rated conversation starter text.
            - ``action`` (str): 'like' or 'dislike'.
            - ``timestamp`` (str): ISO-formatted feedback time.

    Example::

        feedback = load_feedback()
        for entry in feedback:
            icon = "👍" if entry["action"] == "like" else "👎"
            print(f"{icon} {entry['suggestion'][:60]}")
    """
    feedback_path = _get_feedback_path()
    if not feedback_path.exists():
        return []
    try:
        with open(feedback_path, "r", encoding="utf-8") as f:
            all_feedback: List[Dict] = json.load(f)
        result = list(reversed(all_feedback))[:limit]
        logger.debug("load_feedback | returned %d entries", len(result))
        return result
    except (json.JSONDecodeError, IOError) as exc:
        logger.warning("load_feedback | failed to read feedback: %s", exc)
        return []

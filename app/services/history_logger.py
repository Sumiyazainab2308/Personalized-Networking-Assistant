"""
History Logger Service — SmartBridge-compatible module alias.

This module provides persistent storage for conversation sessions as described
in the SmartBridge project specification (Epic 2: Core Functionalities Development).

It wraps the production storage service and provides the exact log_conversation()
and load_history() interface specified in the SmartBridge project documentation.

The history logger operates on a simple append-to-JSON-list pattern:
  1. Adds an ISO-formatted timestamp to the data dictionary
  2. Reads the existing history file (or initializes an empty list)
  3. Appends the new entry
  4. Writes the entire updated list back to disk (atomic write)

pathlib.Path is used for cross-platform file handling (works on Windows,
macOS, and Linux without modification).

Usage:
    from app.services.history_logger import log_conversation, load_history

    log_conversation({
        "event_description": "AI Summit 2024",
        "themes": ["AI", "technology"],
        "suggestions": ["Have you explored...", "What's your take on..."]
    })

    history = load_history()  # Returns list of all saved sessions
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_history_path() -> Path:
    """Return the path to the history JSON file from settings."""
    settings = get_settings()
    return settings.history_path


def log_conversation(data: Dict[str, Any]) -> str:
    """
    Append a conversation session to the persistent history file.

    Adds an ISO-formatted timestamp to the data dictionary (ensuring we
    always know when each conversation was generated), then reads the
    existing history file if it exists, appends the new entry, and writes
    the entire updated list back to disk.

    This read-modify-write pattern ensures data integrity for single-process
    use. The function is thread-safe via the underlying storage service lock.

    Args:
        data: Dictionary containing session data. Recommended fields:
            - ``event_description`` (str): The event description.
            - ``themes`` (List[str]): Extracted themes.
            - ``suggestions`` (List[str]): Generated conversation starters.
            - ``user_interests`` (List[str]): User's stated interests.
            - Any other metadata to persist.

    Returns:
        str: The session_id of the saved record (auto-generated if not provided).

    Example::

        log_conversation({
            "event_description": "Blockchain in Healthcare Summit",
            "themes": ["blockchain", "healthcare"],
            "suggestions": [
                "What do you see as the biggest barrier to blockchain adoption?",
                "Have you seen any successful pilots in clinical data sharing?"
            ],
            "user_interests": ["data privacy", "interoperability"]
        })
    """
    from app.services.storage_service import save_session  # noqa: PLC0415

    # Add ISO-formatted timestamp (as specified in SmartBridge docs)
    data.setdefault("timestamp", datetime.now(tz=timezone.utc).isoformat())

    # Map SmartBridge field names to our storage schema
    normalized = {
        "session_id": data.get("session_id"),
        "event_description": data.get("event_description", ""),
        "user_bio": data.get("user_bio") or _interests_to_bio(data.get("user_interests")),
        "themes": data.get("themes", []),
        "starters": data.get("suggestions", data.get("starters", [])),
        "timestamp": data["timestamp"],
    }
    # Copy any extra fields
    for key, value in data.items():
        if key not in normalized:
            normalized[key] = value

    session_id = save_session(normalized)
    logger.info("log_conversation | session_id=%s | saved", session_id)
    return session_id


def load_history(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Read and return all saved conversation sessions.

    Always returns a list — even when no history has been saved yet
    (returns empty list instead of raising FileNotFoundError).

    Args:
        limit: Maximum number of records to return (most recent first).
            Defaults to 50.

    Returns:
        List[Dict]: List of session dictionaries in reverse chronological order
            (newest first). Each dict contains at minimum:
            - ``session_id``: Unique session identifier.
            - ``event_description``: The event text.
            - ``themes``: List of extracted themes.
            - ``starters``/``suggestions``: Generated conversation starters.
            - ``timestamp``: ISO-formatted creation time.

    Example::

        history = load_history()
        for session in history:
            print(session["event_description"], "—", session["themes"])
    """
    history_path = _get_history_path()
    if not history_path.exists():
        return []
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            all_records: List[Dict] = json.load(f)
        # Return most recent first (reverse chronological)
        result = list(reversed(all_records))[:limit]
        logger.debug("load_history | returned %d records", len(result))
        return result
    except (json.JSONDecodeError, IOError) as exc:
        logger.warning("load_history | failed to read history: %s", exc)
        return []


def _interests_to_bio(interests: Any) -> str | None:
    """Convert a list of interest strings to a bio string."""
    if not interests:
        return None
    if isinstance(interests, list):
        return f"Interests: {', '.join(str(i) for i in interests)}"
    return str(interests)

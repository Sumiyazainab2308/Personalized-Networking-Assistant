"""
Storage Service — Local JSON Persistence.

Provides thread-safe read/write access to JSON files for persisting
interaction history, user profiles, and feedback.

Follows Single Responsibility Principle: this service only handles
local data storage. No business logic lives here.
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.utils.exceptions import StorageError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Thread lock for file I/O safety
_storage_lock = threading.Lock()


def _ensure_data_dir() -> None:
    """Create data directory if it does not exist."""
    settings = get_settings()
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)


def _load_json(filepath: Path) -> List[Dict[str, Any]]:
    """
    Load JSON array from file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        List[Dict[str, Any]]: Parsed JSON array (empty list if file missing).

    Raises:
        StorageError: If file exists but is malformed.
    """
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if not isinstance(data, list):
                raise StorageError("load", f"{filepath} does not contain a JSON array")
            return data
    except json.JSONDecodeError as exc:
        raise StorageError("load", f"JSON decode error in {filepath}: {exc}") from exc
    except OSError as exc:
        raise StorageError("load", str(exc)) from exc


def _save_json(filepath: Path, data: List[Dict[str, Any]]) -> None:
    """
    Write JSON array to file atomically.

    Args:
        filepath: Destination file path.
        data: Python list to serialize.

    Raises:
        StorageError: If writing fails.
    """
    try:
        tmp_path = filepath.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, default=str)
        tmp_path.replace(filepath)  # Atomic rename
    except OSError as exc:
        raise StorageError("save", str(exc)) from exc


# ---------------------------------------------------------------------------
# History operations
# ---------------------------------------------------------------------------


def save_session(session_data: Dict[str, Any]) -> str:
    """
    Persist a new session record to history.

    Args:
        session_data: Dictionary of session fields. A 'session_id' key
                      is auto-generated if not present.

    Returns:
        str: The session_id of the saved record.

    Raises:
        StorageError: If saving fails.
    """
    settings = get_settings()
    _ensure_data_dir()

    session_id = session_data.get("session_id") or str(uuid.uuid4())
    session_data["session_id"] = session_id
    session_data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    with _storage_lock:
        history = _load_json(settings.history_path)
        history.append(session_data)
        # Cap total records to avoid unbounded growth
        if len(history) > settings.max_history_items:
            history = history[-settings.max_history_items :]
        _save_json(settings.history_path, history)

    logger.debug("Session '%s' saved to history.", session_id)
    return session_id


def get_history(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve paginated interaction history, optionally filtered by search term.

    Args:
        page: Page number (1-indexed).
        page_size: Number of items per page.
        search: Optional search term to filter by event_description or themes.

    Returns:
        Dict with 'items', 'total', 'page', 'page_size' keys.
    """
    settings = get_settings()
    _ensure_data_dir()

    with _storage_lock:
        all_items = _load_json(settings.history_path)

    # Reverse so newest items come first
    all_items = list(reversed(all_items))

    if search:
        search_lower = search.lower()
        all_items = [
            item
            for item in all_items
            if search_lower in item.get("event_description", "").lower()
            or search_lower
            in " ".join(item.get("themes", [])).lower()
        ]

    total = len(all_items)
    start = (page - 1) * page_size
    end = start + page_size
    items = all_items[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def update_session_feedback(
    session_id: str,
    rating: int,
    comment: Optional[str] = None,
    starter_index: Optional[int] = None,
) -> bool:
    """
    Attach feedback to an existing session record.

    Args:
        session_id: The session to update.
        rating: Rating value (1–5).
        comment: Optional free-text comment.
        starter_index: Optional index of the rated starter.

    Returns:
        bool: True if the session was found and updated, False otherwise.

    Raises:
        StorageError: If reading or writing fails.
    """
    settings = get_settings()
    _ensure_data_dir()

    with _storage_lock:
        history = _load_json(settings.history_path)
        updated = False

        for item in history:
            if item.get("session_id") == session_id:
                item["feedback_rating"] = rating
                item["feedback_comment"] = comment
                item["feedback_starter_index"] = starter_index
                item["feedback_timestamp"] = datetime.now(timezone.utc).isoformat()
                updated = True
                break

        if updated:
            _save_json(settings.history_path, history)
            logger.debug("Feedback saved for session '%s'.", session_id)
        else:
            logger.warning(
                "Session '%s' not found for feedback update.", session_id
            )

    return updated


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single session record by ID.

    Args:
        session_id: The session ID to look up.

    Returns:
        Optional[Dict]: Session data or None if not found.
    """
    settings = get_settings()
    _ensure_data_dir()

    with _storage_lock:
        history = _load_json(settings.history_path)

    for item in history:
        if item.get("session_id") == session_id:
            return item

    return None


def get_analytics() -> Dict[str, Any]:
    """
    Compute analytics summary from history data.

    Returns:
        Dict with keys: total_sessions, avg_rating, theme_counts,
        sessions_per_day, rated_sessions, unrated_sessions.
    """
    settings = get_settings()
    _ensure_data_dir()

    with _storage_lock:
        all_items = _load_json(settings.history_path)

    total = len(all_items)
    ratings = [
        item["feedback_rating"]
        for item in all_items
        if item.get("feedback_rating") is not None
    ]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

    theme_counts: Dict[str, int] = {}
    sessions_per_day: Dict[str, int] = {}

    for item in all_items:
        for theme in item.get("themes", []):
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        ts = item.get("timestamp", "")
        if ts:
            day = ts[:10]  # YYYY-MM-DD
            sessions_per_day[day] = sessions_per_day.get(day, 0) + 1

    return {
        "total_sessions": total,
        "rated_sessions": len(ratings),
        "unrated_sessions": total - len(ratings),
        "avg_rating": avg_rating,
        "theme_counts": dict(
            sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        ),
        "sessions_per_day": dict(sorted(sessions_per_day.items())),
    }


def clear_history() -> int:
    """
    Delete all history records.

    Returns:
        int: Number of records deleted.
    """
    settings = get_settings()
    _ensure_data_dir()

    with _storage_lock:
        history = _load_json(settings.history_path)
        count = len(history)
        _save_json(settings.history_path, [])

    logger.info("Cleared %d history records.", count)
    return count

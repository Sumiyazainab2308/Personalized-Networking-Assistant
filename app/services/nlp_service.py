"""
NLP Service — DistilBERT / BART Zero-Shot Classification.

Responsible for classifying networking event descriptions into thematic
categories using a zero-shot classification pipeline. Models are loaded
lazily on first use and cached for subsequent calls (Singleton via module-
level variable).

Follows Single Responsibility Principle: this service only classifies text.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from app.config import get_settings
from app.models.responses import ThemeScore
from app.utils.exceptions import ClassificationError, ModelLoadError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Module-level singleton — thread-safe initialization guard
_classifier = None
_classifier_lock = threading.Lock()


def _load_classifier():
    """
    Load the zero-shot classification pipeline (lazy, thread-safe).

    Returns:
        transformers.Pipeline: Zero-shot classification pipeline.

    Raises:
        ModelLoadError: If the model cannot be loaded.
    """
    global _classifier
    if _classifier is None:
        with _classifier_lock:
            if _classifier is None:
                try:
                    from transformers import pipeline  # noqa: PLC0415

                    settings = get_settings()
                    logger.info(
                        "Loading zero-shot classification model: %s",
                        settings.zero_shot_model,
                    )
                    _classifier = pipeline(
                        "zero-shot-classification",
                        model=settings.zero_shot_model,
                        device=-1,  # CPU inference
                    )
                    logger.info("Zero-shot model loaded successfully.")
                except Exception as exc:
                    settings = get_settings()
                    raise ModelLoadError(settings.zero_shot_model, exc) from exc
    return _classifier


def classify_event(
    event_description: str,
    candidate_labels: Optional[List[str]] = None,
) -> List[ThemeScore]:
    """
    Classify an event description into thematic categories.

    Args:
        event_description: Plain-text description of the event.
        candidate_labels: Labels to test against. Defaults to settings labels.

    Returns:
        List[ThemeScore]: Sorted list of theme scores (highest first).

    Raises:
        ClassificationError: If classification fails.
        ModelLoadError: If model loading fails.
    """
    settings = get_settings()
    labels = candidate_labels or settings.event_labels

    if not event_description.strip():
        raise ClassificationError("event_description is empty")

    try:
        classifier = _load_classifier()
        logger.debug("Classifying event description (length=%d)", len(event_description))

        result: Dict = classifier(
            event_description,
            candidate_labels=labels,
            multi_label=True,
        )

        theme_scores = [
            ThemeScore(label=label, score=round(score, 4))
            for label, score in zip(result["labels"], result["scores"])
        ]

        logger.debug(
            "Classification complete. Top theme: %s (%.2f%%)",
            theme_scores[0].label,
            theme_scores[0].score * 100,
        )
        return theme_scores

    except (ModelLoadError, ClassificationError):
        raise
    except Exception as exc:
        logger.error("Classification error: %s", exc, exc_info=True)
        raise ClassificationError(str(exc)) from exc


def get_top_themes(theme_scores: List[ThemeScore], top_n: int = 3) -> List[str]:
    """
    Extract the top-N theme labels from scored results.

    Args:
        theme_scores: Sorted list of ThemeScore objects.
        top_n: Number of top themes to return.

    Returns:
        List[str]: Top-N theme label strings.
    """
    return [ts.label for ts in theme_scores[:top_n]]


def reset_classifier() -> None:
    """
    Reset the cached classifier (useful for testing).

    Forces the next call to `classify_event` to reload the model.
    """
    global _classifier
    with _classifier_lock:
        _classifier = None
    logger.debug("Zero-shot classifier cache cleared.")

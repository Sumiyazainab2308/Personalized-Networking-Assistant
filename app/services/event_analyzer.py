"""
Event Analyzer Service — SmartBridge-compatible module alias.

This module provides the extract_event_themes() interface as described in the
SmartBridge project specification (Epic 2: Core Functionalities Development).

It wraps the production NLP service which uses a BART-large-mnli zero-shot
classification pipeline (functionally equivalent to DistilBERT-based zero-shot
classification but with higher accuracy).

Usage:
    from app.services.event_analyzer import extract_event_themes

    themes = extract_event_themes("AI for Sustainable Cities")
    # Returns: ['technology', 'science', 'social'] (top-3 themes)
"""

from __future__ import annotations

from typing import List, Optional

from app.services.nlp_service import classify_event, get_top_themes
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Default candidate labels matching SmartBridge specification
DEFAULT_LABELS: List[str] = [
    "AI",
    "healthcare",
    "blockchain",
    "education",
    "sustainability",
    "technology",
    "business",
    "finance",
    "marketing",
    "social",
]


def extract_event_themes(
    event_description: str,
    candidate_labels: Optional[List[str]] = None,
    top_n: int = 3,
) -> List[str]:
    """
    Extract the top thematic categories from a networking event description.

    Uses BART-large-mnli zero-shot classification pipeline to score candidate
    labels against the input text and returns the top-N highest-scoring themes.

    The model is loaded once at first call (lazy singleton pattern) and cached
    for subsequent requests to minimize inference latency.

    Args:
        event_description: Plain-text description of the networking event.
            Example: "AI for Sustainable Cities — a summit on smart urban
            infrastructure powered by machine learning."
        candidate_labels: Optional list of category labels to score against.
            Defaults to DEFAULT_LABELS (AI, healthcare, blockchain, etc.).
        top_n: Number of top themes to return. Defaults to 3.

    Returns:
        List[str]: Top-N theme labels ranked by confidence score.
            Example: ['technology', 'AI', 'sustainability']

    Raises:
        ClassificationError: If classification fails.
        ModelLoadError: If the transformer model cannot be loaded.
    """
    labels = candidate_labels or DEFAULT_LABELS
    theme_scores = classify_event(event_description, candidate_labels=labels)
    top = get_top_themes(theme_scores, top_n=top_n)

    logger.info(
        "extract_event_themes | input_len=%d | top_themes=%s",
        len(event_description),
        top,
    )
    return top

"""
Topic Generator Service — SmartBridge-compatible module alias.

This module provides the generate_topics() interface as described in the
SmartBridge project specification (Epic 2: Core Functionalities Development).

It wraps the production generation service which uses GPT-2 Small for
generating context-aware, natural conversation starters for professional
networking events.

Usage:
    from app.services.topic_generator import generate_topics

    starters = generate_topics(
        themes=["AI", "sustainability"],
        interests=["climate change", "urban planning"],
        event_description="AI for Sustainable Cities"
    )
"""

from __future__ import annotations

import random
from typing import List, Optional

from app.services.generation_service import generate_starters
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Fixed random seed for reproducibility (as specified in SmartBridge docs)
random.seed(42)


def generate_topics(
    themes: List[str],
    interests: Optional[List[str]] = None,
    event_description: str = "",
    num_suggestions: int = 3,
    user_bio: Optional[str] = None,
) -> List[str]:
    """
    Generate natural conversation starters using GPT-2 Small.

    Constructs a structured prompt from the extracted event themes and user
    interests, then uses the GPT-2 generation pipeline to produce short,
    engaging opening lines suitable for professional networking.

    The prompt engineering approach guides GPT-2 toward producing responses
    in the desired format — conversation starters rather than arbitrary text.

    Post-processing steps:
      1. Split raw output on newline characters
      2. Extract the first ``num_suggestions`` non-empty lines
      3. Strip bullet markers (*, -, •) and leading/trailing whitespace
      4. Filter blank strings from the result

    Args:
        themes: List of extracted event themes (from event_analyzer).
            Example: ['AI', 'sustainability', 'technology']
        interests: Optional list of user interest keywords to personalize
            the generated starters.
            Example: ['climate change', 'urban planning']
        event_description: Plain-text event description for additional context.
        num_suggestions: Number of conversation starters to generate.
            Defaults to 3 (matching SmartBridge specification).
        user_bio: Optional professional bio string for deeper personalization.

    Returns:
        List[str]: Generated conversation starter strings. Length may be
            less than ``num_suggestions`` if GPT-2 produces fewer valid lines.
            Example:
              [
                "What brought you to explore AI applications for cities?",
                "I'd love to hear your thoughts on sustainable infrastructure.",
                "Have you seen any promising use cases for ML in urban planning?"
              ]

    Raises:
        GenerationError: If text generation fails.
        ModelLoadError: If the GPT-2 model cannot be loaded.
    """
    # Build combined bio string from interests for personalization
    bio_parts = []
    if user_bio:
        bio_parts.append(user_bio)
    if interests:
        bio_parts.append(f"Interests: {', '.join(interests)}")
    combined_bio = " | ".join(bio_parts) or None

    starters = generate_starters(
        themes=themes,
        event_description=event_description,
        user_bio=combined_bio,
        num_starters=num_suggestions,
    )

    logger.info(
        "generate_topics | themes=%s | generated=%d starters",
        themes,
        len(starters),
    )
    return starters

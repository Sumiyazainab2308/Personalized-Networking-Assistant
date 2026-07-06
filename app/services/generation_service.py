"""
Generation Service — GPT-2 Small Conversation Starter Generation.

Responsible for generating personalized conversation starters using a
GPT-2 language model with engineered prompts derived from event themes
and user bio. Models are loaded lazily and cached.

Follows Single Responsibility Principle: this service only generates text.
"""

from __future__ import annotations

import re
import threading
from typing import List, Optional

from app.config import get_settings
from app.utils.exceptions import GenerationError, ModelLoadError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Module-level singleton with thread-safe initialization
_generator = None
_generator_lock = threading.Lock()


def _load_generator():
    """
    Load the GPT-2 text generation pipeline (lazy, thread-safe).

    Returns:
        transformers.Pipeline: Text generation pipeline.

    Raises:
        ModelLoadError: If the model cannot be loaded.
    """
    global _generator
    if _generator is None:
        with _generator_lock:
            if _generator is None:
                try:
                    from transformers import pipeline  # noqa: PLC0415

                    settings = get_settings()
                    logger.info(
                        "Loading text generation model: %s", settings.generation_model
                    )
                    _generator = pipeline(
                        "text-generation",
                        model=settings.generation_model,
                        device=-1,  # CPU inference
                    )
                    logger.info("Text generation model loaded successfully.")
                except Exception as exc:
                    settings = get_settings()
                    raise ModelLoadError(settings.generation_model, exc) from exc
    return _generator


def _build_prompt(
    themes: List[str],
    event_description: str,
    user_bio: Optional[str] = None,
) -> str:
    """
    Build a structured prompt for GPT-2 conversation starter generation.

    Args:
        themes: Top event themes (e.g., ['technology', 'AI']).
        event_description: Plain-text event description.
        user_bio: Optional user bio for personalization.

    Returns:
        str: Formatted prompt string.
    """
    themes_str = ", ".join(themes) if themes else "general networking"
    bio_line = f" My background: {user_bio}." if user_bio else ""
    return (
        f"I'm attending a {themes_str} networking event.{bio_line} "
        f"Event details: {event_description[:200]}. "
        f"Here are some thoughtful, professional conversation starters:\n1."
    )


def _parse_starters(raw_text: str, prompt: str, num_starters: int) -> List[str]:
    """
    Extract clean conversation starters from raw GPT-2 output.

    Args:
        raw_text: Full generated text including the prompt.
        prompt: The original prompt (to strip from the beginning).
        num_starters: Number of starters to return.

    Returns:
        List[str]: Cleaned list of conversation starters.
    """
    # Remove the prompt prefix
    generated = raw_text[len(prompt):]

    # Split on numbered list patterns or newlines
    lines = re.split(r"\n+|\d+\.", generated)
    starters: List[str] = []

    for line in lines:
        cleaned = line.strip()
        # Filter very short or empty lines
        if len(cleaned) > 15:
            # Remove trailing incomplete sentences
            if cleaned.endswith((".", "?", "!")):
                starters.append(cleaned)
            else:
                # Try to find the last sentence boundary
                match = re.search(r"^(.+[.?!])", cleaned)
                if match:
                    starters.append(match.group(1).strip())

        if len(starters) >= num_starters:
            break

    return starters[:num_starters]


def _fallback_starters(themes: List[str], num_starters: int) -> List[str]:
    """
    Provide rule-based fallback starters when GPT-2 output is insufficient.

    Args:
        themes: List of event themes.
        num_starters: Number of starters to produce.

    Returns:
        List[str]: Fallback conversation starters.
    """
    theme = themes[0] if themes else "this field"
    templates = [
        f"What projects are you currently working on in {theme}?",
        f"How did you first get involved in {theme}?",
        f"What trends in {theme} are you most excited about right now?",
        f"What has been your biggest challenge in {theme} this year?",
        f"Are there any tools or frameworks in {theme} you'd recommend?",
        f"What does your typical workday look like in the {theme} space?",
        f"What brought you to this event today?",
        "How has your company adapted to the changes in this industry?",
        "What do you think will be the biggest breakthrough in the next few years?",
        "Are you working on any side projects related to this area?",
    ]
    return templates[:num_starters]


def generate_starters(
    themes: List[str],
    event_description: str,
    user_bio: Optional[str] = None,
    num_starters: int = 5,
) -> List[str]:
    """
    Generate personalized conversation starters using GPT-2.

    Falls back to rule-based templates if GPT-2 output is insufficient.

    Args:
        themes: Top event themes from classification.
        event_description: Plain-text event description.
        user_bio: Optional user bio for personalization.
        num_starters: Number of starters to generate.

    Returns:
        List[str]: Generated conversation starter sentences.

    Raises:
        GenerationError: If text generation encounters a fatal error.
        ModelLoadError: If the GPT-2 model cannot be loaded.
    """
    settings = get_settings()
    prompt = _build_prompt(themes, event_description, user_bio)

    try:
        generator = _load_generator()
        logger.debug(
            "Generating %d conversation starters. Prompt length: %d chars",
            num_starters,
            len(prompt),
        )

        outputs = generator(
            prompt,
            max_new_tokens=settings.max_new_tokens * num_starters,
            num_return_sequences=1,
            temperature=settings.generation_temperature,
            top_p=settings.generation_top_p,
            do_sample=True,
            pad_token_id=50256,  # GPT-2 EOS token as pad
        )

        raw_text: str = outputs[0]["generated_text"]
        starters = _parse_starters(raw_text, prompt, num_starters)

        # If GPT-2 didn't produce enough starters, pad with fallbacks
        if len(starters) < num_starters:
            logger.warning(
                "GPT-2 produced only %d starters; padding with %d fallbacks.",
                len(starters),
                num_starters - len(starters),
            )
            fallbacks = _fallback_starters(themes, num_starters - len(starters))
            starters.extend(fallbacks)

        logger.info("Generated %d conversation starters.", len(starters))
        return starters

    except (ModelLoadError, GenerationError):
        raise
    except Exception as exc:
        logger.error("Generation error: %s", exc, exc_info=True)
        # Return fallbacks on unexpected error to maintain user experience
        logger.warning("Falling back to rule-based starters due to error.")
        return _fallback_starters(themes, num_starters)


def reset_generator() -> None:
    """
    Reset the cached generator (useful for testing).

    Forces the next call to `generate_starters` to reload the model.
    """
    global _generator
    with _generator_lock:
        _generator = None
    logger.debug("Text generation model cache cleared.")

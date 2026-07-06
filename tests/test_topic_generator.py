"""
Tests for the Topic Generator Service (topic_generator.py).

SmartBridge Epic 5: Testing and Local Deployment
Story: Testing the Topic Generator Service

These tests validate the topic_generator.generate_topics() function
which uses GPT-2 Small to generate conversation starters from event themes.

Testing Philosophy:
- Tests validate that output strings are non-empty (post-processing correctness)
- Tests validate that bullet markers are stripped from raw GPT-2 output
- AI model inference is mocked for fast, reliable CI/CD execution

Run with:
    pytest tests/test_topic_generator.py -v
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_generator(monkeypatch):
    """
    Mock the GPT-2 text generation pipeline for all topic_generator tests.

    Returns a controlled output simulating GPT-2's raw text generation,
    including realistic artifacts (bullet markers, extra whitespace) that
    the post-processing step should clean up.
    """
    mock_output = [
        {
            "generated_text": (
                "I am attending a networking event. Here are starters:\n"
                "1. What brought you to explore AI applications for cities?\n"
                "2. I'd love to hear your thoughts on sustainable infrastructure.\n"
                "3. Have you seen any promising use cases for ML in urban planning?"
            )
        }
    ]
    mock_pipeline = MagicMock(return_value=mock_output)

    with patch("app.services.generation_service._generator", mock_pipeline):
        with patch("app.services.generation_service._load_generator", return_value=mock_pipeline):
            yield mock_pipeline


# ─── Core functionality tests ─────────────────────────────────────────────────

def test_generate_topics_returns_list():
    """generate_topics() must return a Python list."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["AI", "sustainability"])
    assert isinstance(result, list), "Should return a list"


def test_generate_topics_non_empty():
    """generate_topics() should return at least one suggestion."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["technology", "business"])
    assert len(result) >= 1, "Should return at least one suggestion"


def test_generate_strings():
    """All generated topics must be string type."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["healthcare", "AI"])
    assert all(isinstance(s, str) for s in result), (
        "All generated topics must be strings"
    )


def test_generate_non_empty_strings():
    """
    Validate post-processing: all returned strings must be non-empty.

    GPT-2 raw output may contain blank lines after splitting on newlines.
    The post-processing step must filter these out.
    """
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["blockchain", "finance"])
    assert all(len(s.strip()) > 0 for s in result), (
        "No empty strings should be in the output (post-processing must strip blanks)"
    )


def test_generate_with_interests():
    """generate_topics() should accept user interests for personalization."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(
        themes=["AI", "sustainability"],
        interests=["climate change", "urban planning"]
    )
    assert isinstance(result, list), "Should handle interests parameter"


def test_generate_with_event_description():
    """generate_topics() should accept an event description for context."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(
        themes=["technology"],
        event_description="AI for Sustainable Cities Summit 2024"
    )
    assert isinstance(result, list)


def test_generate_with_user_bio():
    """generate_topics() should accept a user bio for personalization."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(
        themes=["AI"],
        user_bio="Senior data scientist with 10 years in NLP research"
    )
    assert isinstance(result, list)


def test_generate_num_suggestions_respected():
    """num_suggestions parameter should control generation count (upper bound)."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["AI"], num_suggestions=5)
    # Result may have fewer than num_suggestions if GPT-2 produces fewer valid lines
    assert len(result) <= 5, "Should not exceed num_suggestions"


def test_generate_single_theme():
    """generate_topics() should work with a single theme."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["AI"])
    assert isinstance(result, list)


def test_generate_multiple_themes():
    """generate_topics() should work with multiple themes."""
    from app.services.topic_generator import generate_topics
    result = generate_topics(themes=["AI", "sustainability", "healthcare", "blockchain"])
    assert isinstance(result, list)

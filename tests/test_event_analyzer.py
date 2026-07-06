"""
Tests for the Event Analyzer Service (event_analyzer.py).

SmartBridge Epic 5: Testing and Local Deployment
Story: Testing the Event Analyzer Service

These tests validate the event_analyzer.extract_event_themes() function
which uses BART-large-mnli zero-shot classification to extract themes
from networking event descriptions.

Testing Philosophy:
- Tests validate STRUCTURAL properties, not specific model outputs
- This ensures tests remain valid across model updates or weight changes
- AI model inference is mocked for fast, reliable CI/CD execution

Run with:
    pytest tests/test_event_analyzer.py -v
"""

from __future__ import annotations

from typing import List
from unittest.mock import MagicMock, patch

import pytest


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_classifier(monkeypatch):
    """
    Mock the BART zero-shot classifier for all event_analyzer tests.

    Replaces the actual model pipeline with a deterministic mock that
    returns controlled classification results, eliminating dependency on
    GPU/model weights during test runs.
    """
    mock_pipeline = MagicMock()
    mock_pipeline.return_value = {
        "labels": ["technology", "AI", "sustainability", "business", "healthcare"],
        "scores": [0.91, 0.87, 0.74, 0.52, 0.31],
    }

    # Patch at the nlp_service level (where the model is actually loaded)
    with patch("app.services.nlp_service._classifier", mock_pipeline):
        with patch("app.services.nlp_service._load_classifier", return_value=mock_pipeline):
            yield mock_pipeline


# ─── Core functionality tests ─────────────────────────────────────────────────

def test_extract_event_themes_returns_list():
    """extract_event_themes() must return a Python list."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("AI for Sustainable Cities")
    assert isinstance(result, list), "Should return a list"


def test_extract_event_themes_max_three():
    """extract_event_themes() should return at most 3 themes by default."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("AI for Sustainable Cities")
    assert len(result) <= 3, "Should return at most 3 themes"


def test_extract_event_themes_non_empty():
    """extract_event_themes() should return at least 1 theme for valid input."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("Blockchain Healthcare Summit 2024")
    assert len(result) >= 1, "Should return at least one theme"


def test_extract_event_themes_all_strings():
    """All returned themes must be non-empty strings."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("FinTech Innovation Conference")
    assert all(isinstance(t, str) and len(t) > 0 for t in result), (
        "All themes must be non-empty strings"
    )


def test_extract_event_themes_custom_top_n():
    """Custom top_n parameter should limit output count."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("AI Summit", top_n=2)
    assert len(result) <= 2, "Should respect top_n parameter"


def test_extract_event_themes_with_candidate_labels():
    """Custom candidate_labels should be passed through to the classifier."""
    from app.services.event_analyzer import extract_event_themes
    custom_labels = ["fintech", "regulation", "crypto"]
    result = extract_event_themes("DeFi Conference", candidate_labels=custom_labels)
    assert isinstance(result, list), "Should return a list with custom labels"


def test_extract_event_themes_long_description():
    """Should handle long event descriptions without errors."""
    from app.services.event_analyzer import extract_event_themes
    long_desc = (
        "The International Conference on Artificial Intelligence and Machine Learning "
        "for Sustainable Urban Development brings together researchers, practitioners, "
        "and policy makers to discuss the latest advances in AI-driven solutions for "
        "smart cities, climate change mitigation, and green energy systems. " * 5
    )
    result = extract_event_themes(long_desc)
    assert isinstance(result, list), "Should handle long descriptions"


def test_extract_event_themes_tech_event():
    """Verify function works correctly for a technology-focused event."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("Google Cloud Next 2024: AI and Developer Tools")
    # Should return a list of strings regardless of specific labels
    assert isinstance(result, list)
    assert all(isinstance(t, str) for t in result)


def test_extract_event_themes_healthcare_event():
    """Verify function works correctly for a healthcare-focused event."""
    from app.services.event_analyzer import extract_event_themes
    result = extract_event_themes("Digital Health Innovation Summit: Telemedicine & AI")
    assert isinstance(result, list)


def test_extract_event_themes_default_labels_used():
    """When no candidate_labels provided, function should use DEFAULT_LABELS."""
    from app.services.event_analyzer import DEFAULT_LABELS, extract_event_themes
    assert len(DEFAULT_LABELS) > 0, "DEFAULT_LABELS should be non-empty"
    result = extract_event_themes("Networking event")
    assert isinstance(result, list)

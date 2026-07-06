"""
Tests for the Fact Checker Service (fact_checker.py).

SmartBridge Epic 5: Testing and Local Deployment
Story: Testing the Fact Checker Service

These tests validate the fact_checker.fact_check() function which queries
the Wikipedia REST API to retrieve summarized information about any topic.

Testing Philosophy:
- External network calls are mocked using unittest.mock.patch
- This eliminates dependency on network connectivity and Wikipedia's availability
- Makes tests reliable in any environment including CI/CD pipelines
- All branches of fact_check() are tested: happy path, missing data, error

Run with:
    pytest tests/test_fact_checker.py -v
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests


# ─── Happy path tests ─────────────────────────────────────────────────────────

class TestFactCheckHappyPath:
    """Tests for successful Wikipedia API responses."""

    def test_fact_check_returns_dict(self):
        """fact_check() must return a dictionary."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Artificial intelligence",
            "extract": "Artificial intelligence (AI) is the capability of computational systems.",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Artificial_intelligence"}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("artificial intelligence")

        assert isinstance(result, dict), "Should return a dict"

    def test_fact_check_found_true_when_extract_exists(self):
        """fact_check() should set found=True when Wikipedia returns an extract."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Blockchain",
            "extract": "A blockchain is a distributed ledger with growing lists of records.",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Blockchain"}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("blockchain")

        assert result["found"] is True

    def test_fact_check_returns_extract_text(self):
        """fact_check() should return the Wikipedia extract text."""
        expected_extract = "Machine learning is a subset of artificial intelligence."
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Machine learning",
            "extract": expected_extract,
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Machine_learning"}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("machine learning")

        assert result["extract"] == expected_extract

    def test_fact_check_returns_url(self):
        """fact_check() should return the Wikipedia article URL."""
        expected_url = "https://en.wikipedia.org/wiki/Blockchain"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Blockchain",
            "extract": "A blockchain is a distributed ledger.",
            "content_urls": {"desktop": {"page": expected_url}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("blockchain")

        assert result["url"] == expected_url

    def test_fact_check_confidence_high_when_found(self):
        """fact_check() should set confidence='high' when topic is found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Sustainability",
            "extract": "Sustainability is a social goal for humans to co-exist on Earth.",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Sustainability"}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("sustainability")

        assert result["confidence"] == "high"

    def test_fact_check_preserves_query(self):
        """fact_check() should echo the original query in the response."""
        query = "blockchain in healthcare"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Blockchain",
            "extract": "Blockchain applications in healthcare.",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Blockchain"}},
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check(query)

        assert result["query"] == query


# ─── Missing data / not found tests ───────────────────────────────────────────

class TestFactCheckNotFound:
    """Tests for Wikipedia 404 / not found cases."""

    def test_fact_check_found_false_on_404(self):
        """fact_check() should set found=False when Wikipedia returns 404."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("xyzzy_nonexistent_topic_12345")

        assert result["found"] is False

    def test_fact_check_graceful_on_missing_extract(self):
        """fact_check() should handle missing 'extract' key gracefully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Some Topic",
            "content_urls": {"desktop": {"page": ""}},
            # No 'extract' key
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.services.fact_checker.requests.get", return_value=mock_response):
            from app.services.fact_checker import fact_check
            result = fact_check("obscure topic")

        assert isinstance(result, dict)
        assert "found" in result


# ─── Error / network failure tests ────────────────────────────────────────────

class TestFactCheckErrors:
    """Tests for network errors and exception handling."""

    def test_fact_check_handles_connection_error(self):
        """fact_check() should return a fallback dict on network failure."""
        with patch(
            "app.services.fact_checker.requests.get",
            side_effect=requests.exceptions.ConnectionError("Network unreachable")
        ):
            from app.services.fact_checker import fact_check
            result = fact_check("any topic")

        assert isinstance(result, dict)
        assert result["found"] is False
        assert "extract" in result  # Should have a fallback message

    def test_fact_check_handles_timeout(self):
        """fact_check() should handle request timeouts gracefully."""
        with patch(
            "app.services.fact_checker.requests.get",
            side_effect=requests.exceptions.Timeout("Request timed out")
        ):
            from app.services.fact_checker import fact_check
            result = fact_check("blockchain")

        assert isinstance(result, dict)
        assert result["found"] is False

    def test_fact_check_never_raises_exception(self):
        """fact_check() should NEVER raise an exception — always returns a dict."""
        with patch(
            "app.services.fact_checker.requests.get",
            side_effect=Exception("Unexpected error")
        ):
            from app.services.fact_checker import fact_check
            # Should not raise — defensive programming for production stability
            result = fact_check("any query")

        assert isinstance(result, dict)

"""
Fact Checker Service — SmartBridge-compatible module alias.

This module provides the fact_check() interface as described in the
SmartBridge project specification (Epic 2: Core Functionalities Development).

It wraps the production factcheck service which queries the Wikipedia REST API
to retrieve summarized, reliable information about any topic. No API key or
authentication is required — Wikipedia is publicly accessible.

Usage:
    from app.services.fact_checker import fact_check

    result = fact_check("blockchain in healthcare")
    # Returns a dict with 'extract', 'found', 'url', 'confidence'
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from app.utils.logger import get_logger

logger = get_logger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
REQUEST_TIMEOUT = 10


def fact_check(query: str) -> Dict[str, Any]:
    """
    Verify a topic or claim using the Wikipedia REST API.

    Queries Wikipedia's /page/summary endpoint which returns the first
    paragraph of the most relevant article in JSON format. This provides
    a quick, reliable reference for networking event topics without requiring
    API keys or authentication.

    The try-except block ensures that any network errors, timeout failures,
    or invalid JSON responses are caught gracefully, returning a user-friendly
    fallback message instead of crashing the application.

    Args:
        query: Topic or claim to fact-check.
            Example: "blockchain in healthcare"

    Returns:
        Dict containing:
            - ``found`` (bool): Whether the topic was found on Wikipedia.
            - ``query`` (str): The original query string.
            - ``extract`` (str): First-paragraph summary from Wikipedia,
              or a fallback message if not found.
            - ``url`` (str): Direct Wikipedia article URL (empty if not found).
            - ``confidence`` (str): Confidence level — "high", "medium", or "low".
            - ``title`` (str): Article title as returned by Wikipedia.

    Example::

        >>> result = fact_check("artificial intelligence")
        >>> result["found"]
        True
        >>> result["confidence"]
        'high'
        >>> print(result["extract"][:80])
        Artificial intelligence (AI) is the capability of computational ...
    """
    try:
        # Use the Wikipedia REST API (no authentication required)
        url = WIKIPEDIA_API_URL.format(requests.utils.quote(query, safe=""))
        response = requests.get(
            url,
            headers={"User-Agent": "PersonalizedNetworkingAssistant/1.0"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        extract = data.get("extract", "")
        title = data.get("title", query)
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        if extract:
            logger.info("fact_check | query='%s' | found=True", query)
            return {
                "found": True,
                "query": query,
                "title": title,
                "extract": extract,
                "url": page_url,
                "confidence": "high",
            }
        else:
            return {
                "found": False,
                "query": query,
                "title": title,
                "extract": "No summary available for this topic.",
                "url": page_url,
                "confidence": "low",
            }

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            logger.warning("fact_check | query='%s' | not found on Wikipedia", query)
            return {
                "found": False,
                "query": query,
                "title": query,
                "extract": f"No Wikipedia article found for '{query}'.",
                "url": "",
                "confidence": "low",
            }
        logger.error("fact_check | HTTP error for query='%s': %s", query, e)
        return {
            "found": False,
            "query": query,
            "title": query,
            "extract": "An error occurred while fetching information from Wikipedia.",
            "url": "",
            "confidence": "low",
        }
    except Exception as exc:
        logger.error("fact_check | error for query='%s': %s", query, exc)
        return {
            "found": False,
            "query": query,
            "title": query,
            "extract": "Unable to retrieve information. Please check your internet connection.",
            "url": "",
            "confidence": "low",
        }

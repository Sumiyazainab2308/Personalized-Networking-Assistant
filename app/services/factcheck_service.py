"""
Fact-Check Service — Wikipedia API Integration.

Responsible for querying Wikipedia to verify claims and topics mentioned
in networking event contexts. Returns summaries and source URLs.

Follows Single Responsibility Principle: this service only performs
Wikipedia-based fact verification.
"""

from __future__ import annotations

from typing import List

import wikipediaapi

from app.config import get_settings
from app.models.responses import FactCheckResult
from app.utils.exceptions import FactCheckError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_wiki_client() -> wikipediaapi.Wikipedia:
    """
    Create a Wikipedia API client.

    Returns:
        wikipediaapi.Wikipedia: Configured Wikipedia API client.
    """
    settings = get_settings()
    # Wikipedia-API >= 0.15.0 requires user_agent as first keyword argument
    return wikipediaapi.Wikipedia(
        user_agent="PersonalizedNetworkingAssistant/1.0 (contact@example.com)",
        language=settings.wikipedia_language,
    )


def fact_check_query(query: str) -> FactCheckResult:
    """
    Check a single query against Wikipedia.

    Searches Wikipedia for the given query string. If a page is found,
    extracts a summary excerpt. Determines confidence based on result.

    Args:
        query: The topic or claim to fact-check.

    Returns:
        FactCheckResult: Result with summary, URL, and confidence level.

    Raises:
        FactCheckError: If the Wikipedia API call fails unexpectedly.
    """
    settings = get_settings()

    try:
        wiki = _get_wiki_client()
        logger.debug("Querying Wikipedia for: '%s'", query)

        page = wiki.page(query)

        if page.exists():
            # Get first N sentences of the summary
            sentences = page.summary.split(". ")
            excerpt = ". ".join(sentences[: settings.wikipedia_sentences])
            if not excerpt.endswith("."):
                excerpt += "."

            logger.info("Wikipedia page found for: '%s'", query)
            return FactCheckResult(
                query=query,
                found=True,
                summary=excerpt,
                url=page.fullurl,
                confidence="verified",
            )
        else:
            logger.info("No Wikipedia page found for: '%s'", query)
            return FactCheckResult(
                query=query,
                found=False,
                summary=None,
                url=None,
                confidence="not_found",
            )

    except FactCheckError:
        raise
    except Exception as exc:
        logger.error(
            "Wikipedia API error for query '%s': %s", query, exc, exc_info=True
        )
        raise FactCheckError(query, str(exc)) from exc


def fact_check_multiple(queries: List[str]) -> List[FactCheckResult]:
    """
    Fact-check multiple queries sequentially.

    Failed individual queries are captured as 'not_found' results so
    one failure does not block the entire batch.

    Args:
        queries: List of topics or claims to fact-check.

    Returns:
        List[FactCheckResult]: Results for all queries.
    """
    results: List[FactCheckResult] = []

    for query in queries:
        try:
            result = fact_check_query(query)
            results.append(result)
        except FactCheckError as exc:
            logger.warning("Fact-check failed for '%s': %s", query, exc.message)
            results.append(
                FactCheckResult(
                    query=query,
                    found=False,
                    summary=f"Error: {exc.message}",
                    url=None,
                    confidence="not_found",
                )
            )

    return results

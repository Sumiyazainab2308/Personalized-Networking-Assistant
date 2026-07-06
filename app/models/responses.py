"""
Pydantic response models for all API endpoints.

All API responses are typed and serialized via these models, ensuring
consistent JSON structure across the application.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ThemeScore(BaseModel):
    """A single classified theme with its confidence score."""

    label: str = Field(..., description="Theme label (e.g., 'technology').")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score [0, 1].")


class AnalyzeEventResponse(BaseModel):
    """Response for POST /analyze-event."""

    session_id: str = Field(..., description="Unique session identifier.")
    event_description: str = Field(..., description="Original event description.")
    themes: List[ThemeScore] = Field(
        ..., description="Ranked list of detected event themes."
    )
    top_theme: str = Field(..., description="Highest-confidence theme label.")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="UTC timestamp of analysis."
    )


class ConversationStarterResponse(BaseModel):
    """Response for POST /generate-conversation."""

    session_id: str = Field(..., description="Unique session identifier.")
    starters: List[str] = Field(
        ..., description="Generated conversation starter sentences."
    )
    themes_used: List[str] = Field(
        ..., description="Themes used to generate starters."
    )
    event_description: str = Field(..., description="Original event description.")
    user_bio: Optional[str] = Field(
        default=None, description="User bio if provided."
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="UTC timestamp."
    )


class FactCheckResult(BaseModel):
    """A single Wikipedia fact-check result."""

    query: str = Field(..., description="The query that was fact-checked.")
    found: bool = Field(..., description="Whether a Wikipedia article was found.")
    summary: Optional[str] = Field(
        default=None, description="Wikipedia article summary excerpt."
    )
    url: Optional[str] = Field(
        default=None, description="Wikipedia article URL."
    )
    confidence: str = Field(
        default="unknown",
        description="Confidence level: 'verified', 'partial', or 'not_found'.",
    )


class FactCheckResponse(BaseModel):
    """Response for GET /fact-check."""

    results: List[FactCheckResult] = Field(..., description="List of fact-check results.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HistoryItem(BaseModel):
    """A single entry in the interaction history."""

    session_id: str
    event_description: str
    user_bio: Optional[str] = None
    themes: List[str] = Field(default_factory=list)
    starters: List[str] = Field(default_factory=list)
    feedback_rating: Optional[int] = None
    feedback_comment: Optional[str] = None
    timestamp: datetime
    fact_checks: List[Dict] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    """Response for GET /history."""

    items: List[HistoryItem] = Field(..., description="List of history items.")
    total: int = Field(..., description="Total number of history items.")
    page: int = Field(default=1, description="Current page number.")
    page_size: int = Field(default=20, description="Items per page.")


class FeedbackResponse(BaseModel):
    """Response for POST /feedback."""

    session_id: str
    message: str = Field(..., description="Confirmation message.")
    rating: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str = Field(default="ok")
    version: str
    uptime_seconds: float
    models_loaded: Dict[str, bool] = Field(
        default_factory=dict, description="Indicates which models are loaded."
    )


class ErrorResponse(BaseModel):
    """Standard error response body."""

    error: str = Field(..., description="Error type/category.")
    message: str = Field(..., description="Human-readable error description.")
    status_code: int = Field(..., description="HTTP status code.")

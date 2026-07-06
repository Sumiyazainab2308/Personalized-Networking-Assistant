"""
Pydantic request models for all API endpoints.

All incoming payloads are validated via these models before reaching
the service layer. Field validators enforce business-logic constraints
in addition to type safety.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AnalyzeEventRequest(BaseModel):
    """
    Payload for POST /analyze-event.

    Attributes:
        event_description: Plain-text description of the networking event.
        user_bio: Optional short bio of the user attending the event.
    """

    event_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description of the networking event to analyze.",
        examples=["An AI and machine learning conference focused on NLP advancements."],
    )
    user_bio: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Short professional bio of the user.",
        examples=["Senior software engineer specializing in NLP and distributed systems."],
    )

    @field_validator("event_description")
    @classmethod
    def event_description_not_blank(cls, v: str) -> str:
        """Ensure event_description is not just whitespace."""
        if not v.strip():
            raise ValueError("event_description must not be blank")
        return v.strip()

    @field_validator("user_bio")
    @classmethod
    def user_bio_strip(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from user_bio if provided."""
        if v is not None:
            return v.strip() or None
        return v


class GenerateConversationRequest(BaseModel):
    """
    Payload for POST /generate-conversation.

    Attributes:
        event_description: Plain-text description of the networking event.
        user_bio: Optional professional bio for personalization.
        themes: Optional list of pre-analyzed event themes.
        num_starters: How many conversation starters to generate.
    """

    event_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description of the networking event.",
    )
    user_bio: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Short professional bio of the user.",
    )
    themes: Optional[list[str]] = Field(
        default=None,
        description="Pre-analyzed event themes (skips classification step if provided).",
    )
    num_starters: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of conversation starters to generate (1-10).",
    )

    @field_validator("event_description")
    @classmethod
    def event_description_not_blank(cls, v: str) -> str:
        """Ensure event_description is not just whitespace."""
        if not v.strip():
            raise ValueError("event_description must not be blank")
        return v.strip()


class FeedbackRequest(BaseModel):
    """
    Payload for POST /feedback.

    Attributes:
        session_id: ID of the session to attach feedback to.
        rating: Integer rating from 1 (poor) to 5 (excellent).
        comment: Optional free-text feedback comment.
        starter_index: Optional index of the specific starter being rated.
    """

    session_id: str = Field(
        ...,
        min_length=1,
        description="Session ID to associate feedback with.",
    )
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating from 1 (poor) to 5 (excellent).",
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional free-text feedback comment.",
    )
    starter_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="Index of the specific conversation starter being rated.",
    )


class FactCheckRequest(BaseModel):
    """
    Query parameters / body for GET /fact-check.

    Attributes:
        query: Topic or claim to fact-check via Wikipedia.
    """

    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Topic or claim to fact-check via Wikipedia.",
    )

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        """Ensure query is not just whitespace."""
        if not v.strip():
            raise ValueError("query must not be blank")
        return v.strip()

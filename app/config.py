"""
Application configuration using Pydantic Settings.

All environment variables are loaded from .env file or system environment.
Supports runtime overrides for testing.

List-type env vars (ALLOWED_ORIGINS, EVENT_LABELS) accept comma-separated values:
    ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str) -> List[str]:
    """Split a comma-separated env-var string into a list, stripping whitespace."""
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Personalized Networking Assistant"
    app_version: str = "1.0.0"
    app_description: str = (
        "An AI-powered assistant that analyzes networking events, "
        "generates personalized conversation starters, and verifies facts."
    )
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Stored as a plain comma-separated string in .env to avoid pydantic-settings
    # JSON-parsing of List[str] fields from .env files.
    # Use the `allowed_origins` property to get the parsed list.
    _allowed_origins_raw: str = "http://localhost:8501,http://127.0.0.1:8501"
    allowed_origins_str: str = "http://localhost:8501,http://127.0.0.1:8501"

    # Data persistence
    data_dir: str = "data"
    history_file: str = "history.json"
    profiles_file: str = "profiles.json"

    # NLP Models
    zero_shot_model: str = "facebook/bart-large-mnli"
    generation_model: str = "gpt2"
    max_new_tokens: int = 80
    num_starters: int = 5
    generation_temperature: float = 0.85
    generation_top_p: float = 0.92

    # Event classification labels (comma-separated string, use .event_labels property)
    event_labels_str: str = (
        "technology,business,healthcare,education,finance,"
        "marketing,design,science,art,social"
    )

    # Wikipedia
    wikipedia_language: str = "en"
    wikipedia_sentences: int = 3
    wikipedia_timeout: int = 10

    # History
    max_history_items: int = 1000

    @property
    def allowed_origins(self) -> List[str]:
        """Return ALLOWED_ORIGINS as a list (parsed from comma-separated string)."""
        return _split_csv(self.allowed_origins_str)

    @property
    def event_labels(self) -> List[str]:
        """Return EVENT_LABELS as a list (parsed from comma-separated string)."""
        return _split_csv(self.event_labels_str)

    @property
    def history_path(self) -> Path:
        """Absolute path to the history JSON file."""
        return Path(self.data_dir) / self.history_file

    @property
    def profiles_path(self) -> Path:
        """Absolute path to the profiles JSON file."""
        return Path(self.data_dir) / self.profiles_file


@lru_cache()
def get_settings() -> Settings:
    """
    Return cached application settings.

    Using lru_cache ensures settings are only loaded once per process,
    supporting the Singleton pattern for configuration.

    Returns:
        Settings: The application configuration instance.
    """
    return Settings()

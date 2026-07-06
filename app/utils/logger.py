"""
Centralized logging configuration for the application.

Uses Python's standard logging with structured output format.
All modules should import `get_logger` from here.
"""

import logging
import sys
from typing import Optional

from app.config import get_settings


def setup_logging() -> None:
    """
    Configure root logger with console handler and formatter.

    Should be called once at application startup in main.py.
    Sets the log level from application settings.
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if called multiple times (e.g., in tests)
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Quiet down noisy third-party libraries
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a named logger.

    Args:
        name: Logger name, typically `__name__` of the calling module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name or "networking_assistant")

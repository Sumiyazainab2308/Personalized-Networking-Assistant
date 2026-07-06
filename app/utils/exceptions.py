"""
Custom exception hierarchy for the Personalized Networking Assistant.

All business-logic errors extend `AppBaseException` so FastAPI exception
handlers can catch them uniformly and return consistent JSON error bodies.
"""


class AppBaseException(Exception):
    """
    Base exception for all application-level errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code to return (default 500).
    """

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ModelLoadError(AppBaseException):
    """Raised when an NLP model fails to load from Hugging Face Hub."""

    def __init__(self, model_name: str, original: Exception) -> None:
        super().__init__(
            message=f"Failed to load model '{model_name}': {original}",
            status_code=503,
        )
        self.model_name = model_name
        self.original = original


class GenerationError(AppBaseException):
    """Raised when the text generation service encounters an error."""

    def __init__(self, detail: str) -> None:
        super().__init__(message=f"Text generation failed: {detail}", status_code=500)


class ClassificationError(AppBaseException):
    """Raised when zero-shot classification fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            message=f"Event classification failed: {detail}", status_code=500
        )


class FactCheckError(AppBaseException):
    """Raised when the fact-checking service cannot query Wikipedia."""

    def __init__(self, query: str, detail: str) -> None:
        super().__init__(
            message=f"Fact check failed for query '{query}': {detail}",
            status_code=502,
        )
        self.query = query


class StorageError(AppBaseException):
    """Raised when reading or writing the local JSON data store fails."""

    def __init__(self, operation: str, detail: str) -> None:
        super().__init__(
            message=f"Storage operation '{operation}' failed: {detail}",
            status_code=500,
        )
        self.operation = operation


class ValidationError(AppBaseException):
    """Raised when request payload fails business-logic validation."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"Validation error on field '{field}': {reason}",
            status_code=422,
        )
        self.field = field

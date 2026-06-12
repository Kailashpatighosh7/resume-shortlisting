"""
Custom Exceptions
=================
Application-specific HTTP exceptions for clean error handling.
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(HTTPException):
    """Raised when authentication fails or token is invalid."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    """Raised when the user lacks permission for the requested action."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationException(HTTPException):
    """Raised when request data fails validation."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class ConflictException(HTTPException):
    """Raised when a resource already exists (e.g. duplicate email)."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class FileProcessingException(HTTPException):
    """Raised when file upload or parsing fails."""

    def __init__(self, detail: str = "File processing error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )

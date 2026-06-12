"""
API Dependencies
================
Shared dependencies for FastAPI route injection.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_recruiter_id(
    token: str = Depends(oauth2_scheme),
) -> int:
    """
    Decode JWT token and return the authenticated recruiter ID.

    Raises:
        UnauthorizedException: If token is missing or invalid.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    recruiter_id = payload.get("sub")
    if recruiter_id is None:
        raise UnauthorizedException("Invalid token payload")

    try:
        return int(recruiter_id)
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid token payload")

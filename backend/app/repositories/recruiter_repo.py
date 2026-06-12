"""
Recruiter Repository
====================
Database operations for the Recruiter entity.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recruiter import Recruiter


class RecruiterRepository:
    """Data access layer for recruiters."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, recruiter_id: int) -> Optional[Recruiter]:
        """Fetch a recruiter by primary key."""
        result = await self.db.execute(
            select(Recruiter).where(Recruiter.id == recruiter_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Recruiter]:
        """Fetch a recruiter by email address."""
        result = await self.db.execute(
            select(Recruiter).where(Recruiter.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, recruiter: Recruiter) -> Recruiter:
        """Persist a new recruiter."""
        self.db.add(recruiter)
        await self.db.flush()
        await self.db.refresh(recruiter)
        return recruiter

    async def update(self, recruiter: Recruiter) -> Recruiter:
        """Update an existing recruiter (already attached to session)."""
        await self.db.flush()
        await self.db.refresh(recruiter)
        return recruiter

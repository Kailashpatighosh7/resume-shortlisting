"""
Email Repository
================
"""

from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_sent import EmailSent


class EmailRepository:
    """Data access layer for email logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, email_id: int) -> EmailSent | None:
        result = await self.db.execute(
            select(EmailSent).where(EmailSent.id == email_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        email_type: str | None = None,
        job_id: int | None = None,
        limit: int = 100,
    ) -> List[EmailSent]:
        query = select(EmailSent)
        if email_type:
            query = query.where(EmailSent.email_type == email_type)
        if job_id:
            query = query.where(EmailSent.job_id == job_id)
        query = query.order_by(EmailSent.sent_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_by_candidate(self, candidate_id: int) -> List[EmailSent]:
        result = await self.db.execute(
            select(EmailSent)
            .where(EmailSent.candidate_id == candidate_id)
            .order_by(EmailSent.sent_at.desc())
        )
        return result.scalars().all()

    async def create(self, email: EmailSent) -> EmailSent:
        self.db.add(email)
        await self.db.flush()
        await self.db.refresh(email)
        return email

    async def count_all(self) -> int:
        result = await self.db.execute(select(func.count(EmailSent.id)))
        return result.scalar() or 0

    async def count_by_status(self, status: str) -> int:
        result = await self.db.execute(
            select(func.count(EmailSent.id)).where(EmailSent.status == status)
        )
        return result.scalar() or 0

    async def count_by_type(self, email_type: str) -> int:
        result = await self.db.execute(
            select(func.count(EmailSent.id)).where(EmailSent.email_type == email_type)
        )
        return result.scalar() or 0

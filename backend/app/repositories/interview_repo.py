"""
Interview Repository
====================
"""

from typing import Optional, List, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview


class InterviewRepository:
    """Data access layer for interviews."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, interview_id: int) -> Optional[Interview]:
        result = await self.db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        return result.scalar_one_or_none()

    async def list_by_recruiter(
        self,
        recruiter_id: int,
        status: Optional[str] = None,
    ) -> List[Interview]:
        query = select(Interview).where(Interview.recruiter_id == recruiter_id)
        if status:
            query = query.where(Interview.status == status)
        query = query.order_by(Interview.scheduled_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_all(
        self,
        status: Optional[str] = None,
    ) -> List[Interview]:
        query = select(Interview)
        if status:
            query = query.where(Interview.status == status)
        query = query.order_by(Interview.scheduled_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, interview: Interview) -> Interview:
        self.db.add(interview)
        await self.db.flush()
        await self.db.refresh(interview)
        return interview

    async def update(self, interview: Interview) -> Interview:
        await self.db.flush()
        await self.db.refresh(interview)
        return interview

    async def delete(self, interview_id: int) -> bool:
        result = await self.db.execute(
            delete(Interview).where(Interview.id == interview_id)
        )
        return result.rowcount > 0

    async def count_all(self) -> int:
        result = await self.db.execute(select(func.count(Interview.id)))
        return result.scalar() or 0

    async def count_by_status(self, status: str) -> int:
        result = await self.db.execute(
            select(func.count(Interview.id)).where(Interview.status == status)
        )
        return result.scalar() or 0

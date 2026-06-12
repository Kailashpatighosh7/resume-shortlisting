"""
Resume Repository
=================
"""

from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    """Data access layer for resumes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, resume_id: int) -> Optional[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        return result.scalar_one_or_none()

    async def get_by_candidate_id(self, candidate_id: int) -> Optional[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.candidate_id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def list_by_candidate_ids(self, candidate_ids: List[int]) -> List[Resume]:
        if not candidate_ids:
            return []
        result = await self.db.execute(
            select(Resume).where(Resume.candidate_id.in_(candidate_ids))
        )
        return result.scalars().all()

    async def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def update(self, resume: Resume) -> Resume:
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def delete(self, resume_id: int) -> bool:
        result = await self.db.execute(
            delete(Resume).where(Resume.id == resume_id)
        )
        return result.rowcount > 0

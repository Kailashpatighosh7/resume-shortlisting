"""
Job Repository
==============
"""

from typing import Optional, List, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job
from app.models.candidate import Candidate


class JobRepository:
    """Data access layer for jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, job_id: int) -> Optional[Job]:
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_with_candidates(self, job_id: int) -> Optional[Job]:
        result = await self.db.execute(
            select(Job)
            .options(selectinload(Job.candidates))
            .where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_by_recruiter(
        self,
        recruiter_id: int,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Job], int]:
        """List jobs with pagination, filtering, and search."""
        query = select(Job).where(Job.recruiter_id == recruiter_id)
        count_query = select(func.count(Job.id)).where(Job.recruiter_id == recruiter_id)

        if status:
            query = query.where(Job.status == status)
            count_query = count_query.where(Job.status == status)
        if search:
            query = query.where(Job.title.ilike(f"%{search}%"))
            count_query = count_query.where(Job.title.ilike(f"%{search}%"))

        query = query.order_by(Job.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        total_result = await self.db.execute(count_query)

        return result.scalars().all(), total_result.scalar()

    async def create(self, job: Job) -> Job:
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def update(self, job: Job) -> Job:
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete(self, job_id: int) -> bool:
        result = await self.db.execute(
            delete(Job).where(Job.id == job_id)
        )
        return result.rowcount > 0

    async def get_candidate_count(self, job_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Candidate.id)).where(Candidate.job_id == job_id)
        )
        return result.scalar() or 0

    async def count_by_recruiter(self, recruiter_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Job.id)).where(Job.recruiter_id == recruiter_id)
        )
        return result.scalar() or 0

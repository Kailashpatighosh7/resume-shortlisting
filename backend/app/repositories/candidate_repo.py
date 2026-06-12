"""
Candidate Repository
====================
"""

from typing import Optional, List, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.candidate_score import CandidateScore


class CandidateRepository:
    """Data access layer for candidates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, candidate_id: int) -> Optional[Candidate]:
        result = await self.db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def get_with_details(self, candidate_id: int) -> Optional[Candidate]:
        result = await self.db.execute(
            select(Candidate)
            .options(
                selectinload(Candidate.resume),
                selectinload(Candidate.scores),
            )
            .where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def list_by_job(
        self,
        job_id: int,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Candidate], int]:
        query = select(Candidate).where(Candidate.job_id == job_id)
        count_query = select(func.count(Candidate.id)).where(Candidate.job_id == job_id)

        if status:
            query = query.where(Candidate.status == status)
            count_query = count_query.where(Candidate.status == status)
        if search:
            query = query.where(Candidate.name.ilike(f"%{search}%"))
            count_query = count_query.where(Candidate.name.ilike(f"%{search}%"))

        query = query.order_by(Candidate.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        total_result = await self.db.execute(count_query)

        return result.scalars().all(), total_result.scalar()

    async def list_all(
        self,
        page: int = 1,
        per_page: int = 50,
        search: Optional[str] = None,
    ) -> Tuple[List[Candidate], int]:
        query = select(Candidate)
        count_query = select(func.count(Candidate.id))

        if search:
            query = query.where(Candidate.name.ilike(f"%{search}%"))
            count_query = count_query.where(Candidate.name.ilike(f"%{search}%"))

        query = query.order_by(Candidate.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        total_result = await self.db.execute(count_query)

        return result.scalars().all(), total_result.scalar()

    async def create(self, candidate: Candidate) -> Candidate:
        self.db.add(candidate)
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def update(self, candidate: Candidate) -> Candidate:
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def delete(self, candidate_id: int) -> bool:
        result = await self.db.execute(
            delete(Candidate).where(Candidate.id == candidate_id)
        )
        return result.rowcount > 0

    async def count_all(self) -> int:
        result = await self.db.execute(select(func.count(Candidate.id)))
        return result.scalar() or 0

    async def count_by_status(self, status: str) -> int:
        result = await self.db.execute(
            select(func.count(Candidate.id)).where(Candidate.status == status)
        )
        return result.scalar() or 0

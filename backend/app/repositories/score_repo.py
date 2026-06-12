"""
Score Repository
================
"""

from typing import Optional, List

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_score import CandidateScore


class ScoreRepository:
    """Data access layer for candidate scores."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, score_id: int) -> Optional[CandidateScore]:
        result = await self.db.execute(
            select(CandidateScore).where(CandidateScore.id == score_id)
        )
        return result.scalar_one_or_none()

    async def get_by_candidate_and_job(
        self, candidate_id: int, job_id: int
    ) -> Optional[CandidateScore]:
        result = await self.db.execute(
            select(CandidateScore).where(
                CandidateScore.candidate_id == candidate_id,
                CandidateScore.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_job(self, job_id: int) -> List[CandidateScore]:
        result = await self.db.execute(
            select(CandidateScore)
            .where(CandidateScore.job_id == job_id)
            .order_by(CandidateScore.overall_score.desc())
        )
        return result.scalars().all()

    async def create(self, score: CandidateScore) -> CandidateScore:
        self.db.add(score)
        await self.db.flush()
        await self.db.refresh(score)
        return score

    async def upsert(self, score: CandidateScore) -> CandidateScore:
        """Create or update a score entry."""
        existing = await self.get_by_candidate_and_job(
            score.candidate_id, score.job_id
        )
        if existing:
            existing.overall_score = score.overall_score
            existing.matched_skills = score.matched_skills
            existing.missing_skills = score.missing_skills
            existing.semantic_matches = score.semantic_matches
            existing.explanation = score.explanation
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(score)

    async def delete_by_job(self, job_id: int) -> int:
        result = await self.db.execute(
            delete(CandidateScore).where(CandidateScore.job_id == job_id)
        )
        return result.rowcount

    async def average_score(self) -> float:
        result = await self.db.execute(
            select(func.avg(CandidateScore.overall_score))
        )
        return result.scalar() or 0.0

    async def score_distribution(self) -> List[dict]:
        """Get distribution of scores in ranges."""
        result = await self.db.execute(
            select(CandidateScore.overall_score)
        )
        scores = [r for r in result.scalars().all()]
        if not scores:
            return []

        buckets = {
            "0-20%": 0, "20-40%": 0, "40-60%": 0,
            "60-80%": 0, "80-100%": 0,
        }
        for s in scores:
            pct = s * 100
            if pct < 20:
                buckets["0-20%"] += 1
            elif pct < 40:
                buckets["20-40%"] += 1
            elif pct < 60:
                buckets["40-60%"] += 1
            elif pct < 80:
                buckets["60-80%"] += 1
            else:
                buckets["80-100%"] += 1

        return [{"range": k, "count": v} for k, v in buckets.items()]

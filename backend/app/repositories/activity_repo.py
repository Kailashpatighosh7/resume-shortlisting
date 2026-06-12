"""
Activity Log Repository
=======================
"""

from typing import List

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog


class ActivityRepository:
    """Data access layer for activity logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: ActivityLog) -> ActivityLog:
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def list_by_recruiter(
        self,
        recruiter_id: int,
        limit: int = 50,
    ) -> List[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .where(ActivityLog.recruiter_id == recruiter_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_recent(self, limit: int = 20) -> List[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def monthly_counts(self) -> List[dict]:
        """Get monthly activity counts for the past 12 months."""
        result = await self.db.execute(
            select(
                func.to_char(ActivityLog.created_at, 'YYYY-MM').label('month'),
                func.count(ActivityLog.id).label('count'),
            )
            .group_by('month')
            .order_by('month')
            .limit(12)
        )
        return [{"month": row.month, "count": row.count} for row in result]

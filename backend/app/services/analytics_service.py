"""
Analytics Service
=================
Aggregation queries for the HR analytics dashboard.
"""

from collections import Counter

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.candidate_score import CandidateScore
from app.models.email_sent import EmailSent
from app.repositories.job_repo import JobRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.interview_repo import InterviewRepository
from app.repositories.score_repo import ScoreRepository
from app.repositories.email_repo import EmailRepository
from app.schemas.analytics import (
    DashboardStats,
    SkillFrequency,
    MonthlyActivity,
    AnalyticsDashboardResponse,
)


class AnalyticsService:
    """Generates analytics data for the HR dashboard."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.interview_repo = InterviewRepository(db)
        self.score_repo = ScoreRepository(db)
        self.email_repo = EmailRepository(db)

    async def get_dashboard(self, recruiter_id: int) -> AnalyticsDashboardResponse:
        """Get full analytics dashboard data."""
        stats = await self._get_stats(recruiter_id)
        top_skills = await self._get_top_skills(recruiter_id)
        monthly = await self._get_monthly_activity(recruiter_id)
        score_dist = await self.score_repo.score_distribution()
        status_dist = await self._get_status_distribution()

        return AnalyticsDashboardResponse(
            stats=stats,
            top_skills=top_skills,
            monthly_activity=monthly,
            score_distribution=score_dist,
            status_distribution=status_dist,
        )

    async def _get_stats(self, recruiter_id: int) -> DashboardStats:
        """Compute high-level statistics."""
        total_jobs = await self.job_repo.count_by_recruiter(recruiter_id)
        total_candidates = await self.candidate_repo.count_all()
        total_interviews = await self.interview_repo.count_all()
        avg_score = await self.score_repo.average_score()
        shortlisted = await self.candidate_repo.count_by_status("shortlisted")
        emails_sent = await self.email_repo.count_all()

        # Interview conversion: scheduled -> completed
        completed = await self.interview_repo.count_by_status("completed")
        conversion = (completed / total_interviews * 100) if total_interviews > 0 else 0

        return DashboardStats(
            total_jobs=total_jobs,
            total_candidates=total_candidates,
            total_interviews=total_interviews,
            average_match_score=round(avg_score * 100, 1),
            shortlisted_candidates=shortlisted,
            interview_conversion_rate=round(conversion, 1),
            emails_sent=emails_sent,
        )

    async def _get_top_skills(self, recruiter_id: int) -> list[SkillFrequency]:
        """Get most frequently required skills across all jobs."""
        result = await self.db.execute(
            select(Job.required_skills).where(Job.recruiter_id == recruiter_id)
        )
        all_skills_raw = result.scalars().all()

        skill_counter = Counter()
        for skills_str in all_skills_raw:
            if skills_str:
                for skill in skills_str.split(","):
                    s = skill.strip().lower()
                    if s:
                        skill_counter[s.title()] += 1

        top = skill_counter.most_common(10)
        return [SkillFrequency(skill=s, count=c) for s, c in top]

    async def _get_monthly_activity(self, recruiter_id: int) -> list[MonthlyActivity]:
        """Get monthly job creation and candidate activity."""
        # Jobs per month
        jobs_result = await self.db.execute(
            select(
                func.to_char(Job.created_at, 'YYYY-MM').label('month'),
                func.count(Job.id).label('count'),
            )
            .where(Job.recruiter_id == recruiter_id)
            .group_by('month')
            .order_by('month')
        )
        jobs_by_month = {r.month: r.count for r in jobs_result}

        # Candidates per month
        cands_result = await self.db.execute(
            select(
                func.to_char(Candidate.created_at, 'YYYY-MM').label('month'),
                func.count(Candidate.id).label('count'),
            )
            .group_by('month')
            .order_by('month')
        )
        cands_by_month = {r.month: r.count for r in cands_result}

        # Interviews per month
        ivs_result = await self.db.execute(
            select(
                func.to_char(Interview.created_at, 'YYYY-MM').label('month'),
                func.count(Interview.id).label('count'),
            )
            .group_by('month')
            .order_by('month')
        )
        ivs_by_month = {r.month: r.count for r in ivs_result}

        all_months = sorted(
            set(jobs_by_month.keys()) | set(cands_by_month.keys()) | set(ivs_by_month.keys())
        )

        return [
            MonthlyActivity(
                month=m,
                jobs_created=jobs_by_month.get(m, 0),
                candidates_added=cands_by_month.get(m, 0),
                interviews_scheduled=ivs_by_month.get(m, 0),
            )
            for m in all_months[-12:]  # Last 12 months
        ]

    async def _get_status_distribution(self) -> list[dict]:
        """Get candidate status distribution."""
        result = await self.db.execute(
            select(
                Candidate.status,
                func.count(Candidate.id).label('count'),
            )
            .group_by(Candidate.status)
        )
        return [{"status": r.status, "count": r.count} for r in result]

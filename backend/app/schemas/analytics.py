"""
Analytics Schemas
=================
"""

from typing import List

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """High-level dashboard statistics."""
    total_jobs: int = 0
    total_candidates: int = 0
    total_interviews: int = 0
    average_match_score: float = 0.0
    shortlisted_candidates: int = 0
    interview_conversion_rate: float = 0.0
    emails_sent: int = 0


class SkillFrequency(BaseModel):
    """Skill with count."""
    skill: str
    count: int


class MonthlyActivity(BaseModel):
    """Monthly aggregate data point."""
    month: str  # YYYY-MM
    jobs_created: int = 0
    candidates_added: int = 0
    interviews_scheduled: int = 0


class AnalyticsDashboardResponse(BaseModel):
    """Full analytics dashboard data."""
    stats: DashboardStats
    top_skills: List[SkillFrequency] = []
    monthly_activity: List[MonthlyActivity] = []
    score_distribution: List[dict] = []
    status_distribution: List[dict] = []

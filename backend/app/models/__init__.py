"""
Models Package
==============
Import all ORM models here so Alembic and SQLAlchemy can discover them.
"""

from app.models.recruiter import Recruiter
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.candidate_score import CandidateScore
from app.models.interview import Interview
from app.models.email_sent import EmailSent
from app.models.activity_log import ActivityLog

__all__ = [
    "Recruiter",
    "Job",
    "Candidate",
    "Resume",
    "CandidateScore",
    "Interview",
    "EmailSent",
    "ActivityLog",
]

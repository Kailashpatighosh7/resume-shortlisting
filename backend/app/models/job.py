"""
Job Model
=========
Stores job postings created by recruiters.
Includes the pre-computed JD embedding for semantic matching.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Index,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Job(Base):
    """Job posting / description entity."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recruiter_id = Column(
        Integer, ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True, default="")
    required_skills = Column(Text, nullable=False, default="")  # comma-separated
    preferred_skills = Column(Text, nullable=True, default="")  # comma-separated
    min_experience = Column(Integer, nullable=True, default=0)
    education = Column(String(255), nullable=True, default="")
    location = Column(String(255), nullable=True, default="")
    description = Column(Text, nullable=False)
    status = Column(
        String(50), nullable=False, default="open"
    )  # open, closed, draft
    shortlist_quota = Column(Integer, nullable=False, default=5)
    jd_embedding = Column(Text, nullable=True)  # JSON-serialised float array

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────
    recruiter = relationship("Recruiter", back_populates="jobs")
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")
    candidate_scores = relationship("CandidateScore", back_populates="job", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="job", cascade="all, delete-orphan")
    emails_sent = relationship("EmailSent", back_populates="job", cascade="all, delete-orphan")

    # ── Table-level indexes ───────────────────────────────
    __table_args__ = (
        Index("ix_jobs_recruiter_status", "recruiter_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title!r}>"

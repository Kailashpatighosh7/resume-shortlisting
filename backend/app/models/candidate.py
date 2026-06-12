"""
Candidate Model
===============
Stores candidate information, linked to a specific job posting.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database.base import Base


class Candidate(Base):
    """A candidate who applied (or whose resume was uploaded) for a job."""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, default="")
    phone = Column(String(50), nullable=True, default="")
    status = Column(
        String(50), nullable=False, default="new"
    )  # new, shortlisted, rejected, interview, hired

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
    job = relationship("Job", back_populates="candidates")
    resume = relationship(
        "Resume", back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    scores = relationship(
        "CandidateScore", back_populates="candidate", cascade="all, delete-orphan"
    )
    interviews = relationship(
        "Interview", back_populates="candidate", cascade="all, delete-orphan"
    )
    emails_sent = relationship(
        "EmailSent", back_populates="candidate", cascade="all, delete-orphan"
    )

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_candidates_job_status", "job_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} name={self.name!r}>"

"""
Interview Model
===============
Stores scheduled interview details.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Index,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Interview(Base):
    """Interview scheduled between recruiter and candidate."""

    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(
        Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recruiter_id = Column(
        Integer, ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    mode = Column(
        String(50), nullable=False, default="video"
    )  # in-person, video, phone
    meeting_link = Column(String(500), nullable=True, default="")
    status = Column(
        String(50), nullable=False, default="scheduled"
    )  # scheduled, completed, cancelled
    notes = Column(Text, nullable=True, default="")

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
    candidate = relationship("Candidate", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    recruiter = relationship("Recruiter", back_populates="interviews")

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_interviews_scheduled", "scheduled_at"),
        Index("ix_interviews_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Interview id={self.id} status={self.status}>"

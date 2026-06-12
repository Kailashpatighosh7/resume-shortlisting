"""
Activity Log Model
==================
Tracks recruiter actions for audit trail and analytics.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.database.base import Base


class ActivityLog(Base):
    """Audit log of recruiter actions within the system."""

    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recruiter_id = Column(
        Integer, ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action = Column(String(100), nullable=False)  # e.g. "created_job", "uploaded_resume"
    entity_type = Column(String(50), nullable=True)  # e.g. "job", "candidate"
    entity_id = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────
    recruiter = relationship("Recruiter", back_populates="activity_logs")

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_activity_recruiter_date", "recruiter_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} action={self.action!r}>"

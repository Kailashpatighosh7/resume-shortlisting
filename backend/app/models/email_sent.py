"""
Email Sent Model
================
Logs all emails sent through the system for audit and history.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database.base import Base


class EmailSent(Base):
    """Record of an email sent to a candidate."""

    __tablename__ = "emails_sent"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(
        Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email_type = Column(
        String(50), nullable=False
    )  # shortlisted, rejected, interview_scheduled
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(
        String(50), nullable=False, default="sent"
    )  # sent, failed, pending
    sent_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────
    candidate = relationship("Candidate", back_populates="emails_sent")
    job = relationship("Job", back_populates="emails_sent")

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_emails_candidate", "candidate_id"),
        Index("ix_emails_type", "email_type"),
    )

    def __repr__(self) -> str:
        return f"<EmailSent id={self.id} type={self.email_type}>"

"""
Candidate Score Model
=====================
Stores the semantic match score and explainability data
between a candidate's resume and a job description.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey, JSON, Index,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class CandidateScore(Base):
    """Semantic match score with explainability breakdown."""

    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(
        Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id = Column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    overall_score = Column(Float, nullable=False, default=0.0)

    # Explainability fields (JSON arrays / objects)
    matched_skills = Column(JSON, nullable=True, default=list)
    missing_skills = Column(JSON, nullable=True, default=list)
    semantic_matches = Column(JSON, nullable=True, default=list)
    explanation = Column(JSON, nullable=True, default=dict)

    scored_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────
    candidate = relationship("Candidate", back_populates="scores")
    job = relationship("Job", back_populates="candidate_scores")

    # ── Indexes ───────────────────────────────────────────
    __table_args__ = (
        Index("ix_scores_job_score", "job_id", "overall_score"),
    )

    def __repr__(self) -> str:
        return f"<CandidateScore id={self.id} score={self.overall_score:.2f}>"

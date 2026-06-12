"""
Resume Model
============
Stores uploaded resume files and their parsed content.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base


class Resume(Base):
    """Resume document with parsed content and embedding vector."""

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    parsed_text = Column(Text, nullable=True, default="")
    parsed_data = Column(JSON, nullable=True)  # structured extraction result
    resume_embedding = Column(Text, nullable=True)  # JSON-serialised float array

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────
    candidate = relationship("Candidate", back_populates="resume")

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file={self.original_filename!r}>"

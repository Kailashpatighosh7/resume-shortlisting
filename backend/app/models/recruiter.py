"""
Recruiter Model
===============
Stores recruiter account information for authentication.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database.base import Base


class Recruiter(Base):
    """Recruiter user account."""

    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True, default="")
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
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="recruiter")
    activity_logs = relationship(
        "ActivityLog", back_populates="recruiter", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Recruiter id={self.id} email={self.email}>"

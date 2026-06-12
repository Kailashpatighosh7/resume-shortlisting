"""
Interview Schemas
=================
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class InterviewCreate(BaseModel):
    """Schedule a new interview."""
    candidate_id: int
    job_id: int
    scheduled_at: datetime
    mode: str = Field(default="video", pattern="^(in-person|video|phone)$")
    meeting_link: str = Field(default="", max_length=500)
    notes: str = Field(default="")


class InterviewUpdate(BaseModel):
    """Update interview details."""
    scheduled_at: Optional[datetime] = None
    mode: Optional[str] = Field(None, pattern="^(in-person|video|phone)$")
    meeting_link: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|completed|cancelled)$")
    notes: Optional[str] = None


class InterviewResponse(BaseModel):
    """Interview response."""
    id: int
    candidate_id: int
    job_id: int
    recruiter_id: int
    scheduled_at: datetime
    mode: str
    meeting_link: str
    status: str
    notes: str
    candidate_name: str = ""
    job_title: str = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InterviewListResponse(BaseModel):
    """Paginated interview list."""
    items: List[InterviewResponse]
    total: int

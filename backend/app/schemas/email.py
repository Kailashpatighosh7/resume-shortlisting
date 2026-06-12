"""
Email Schemas
=============
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class SendEmailRequest(BaseModel):
    """Manual email send request."""
    candidate_id: int
    job_id: int
    email_type: str = Field(..., pattern="^(shortlisted|rejected|interview_scheduled|custom)$")
    subject: Optional[str] = None
    body: Optional[str] = None


class EmailLogResponse(BaseModel):
    """Email log entry."""
    id: int
    candidate_id: int
    job_id: int
    email_type: str
    recipient_email: str
    subject: str
    body: str
    status: str
    sent_at: datetime

    model_config = {"from_attributes": True}


class EmailLogListResponse(BaseModel):
    """Email log list."""
    items: List[EmailLogResponse]
    total: int


class EmailStatsResponse(BaseModel):
    """Aggregated email sending statistics."""
    total: int = 0
    sent: int = 0
    failed: int = 0
    shortlisted: int = 0
    rejected: int = 0
    interview_scheduled: int = 0
    custom: int = 0

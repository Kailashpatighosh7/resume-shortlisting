"""
Email Endpoints
===============
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.email_service import EmailService
from app.schemas.email import (
    SendEmailRequest, EmailLogResponse, EmailLogListResponse, EmailStatsResponse,
)

router = APIRouter()


@router.get("/stats", response_model=EmailStatsResponse)
async def get_email_stats(
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get email sending statistics."""
    service = EmailService(db)
    return await service.get_stats()


@router.get("", response_model=EmailLogListResponse)
async def list_emails(
    email_type: Optional[str] = None,
    job_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """List email logs."""
    service = EmailService(db)
    return await service.list_emails(email_type, job_id, limit)


@router.post("/send", response_model=EmailLogResponse, status_code=201)
async def send_email(
    data: SendEmailRequest,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Send an email notification to a candidate."""
    service = EmailService(db)
    return await service.send_notification(
        candidate_id=data.candidate_id,
        job_id=data.job_id,
        email_type=data.email_type,
        custom_subject=data.subject,
        custom_body=data.body,
    )

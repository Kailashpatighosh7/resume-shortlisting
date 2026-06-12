"""
Interview Endpoints
===================
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.interview_service import InterviewService
from app.schemas.interview import (
    InterviewCreate, InterviewUpdate, InterviewResponse, InterviewListResponse,
)

router = APIRouter()


@router.get("", response_model=InterviewListResponse)
async def list_interviews(
    status: Optional[str] = None,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """List all interviews."""
    service = InterviewService(db)
    return await service.list_interviews(recruiter_id, status)


@router.post("", response_model=InterviewResponse, status_code=201)
async def create_interview(
    data: InterviewCreate,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a new interview (sends email notification automatically)."""
    service = InterviewService(db)
    return await service.create_interview(recruiter_id, data)


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Update interview details or status."""
    service = InterviewService(db)
    return await service.update_interview(interview_id, data)


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Cancel and delete an interview."""
    service = InterviewService(db)
    await service.delete_interview(interview_id)
    return {"message": f"Interview #{interview_id} cancelled"}

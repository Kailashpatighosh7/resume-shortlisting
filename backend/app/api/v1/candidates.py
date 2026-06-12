"""
Candidate Endpoints
===================
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.candidate_service import CandidateService
from app.schemas.candidate import CandidateUpdate, CandidateDetailResponse, CandidateListResponse

router = APIRouter()


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    job_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    search: Optional[str] = None,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """List candidates, optionally filtered by job."""
    service = CandidateService(db)
    if job_id:
        return await service.list_candidates_by_job(job_id, page, per_page, status, search)
    return await service.list_all_candidates(page, per_page, search)


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(
    candidate_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get candidate details with resume and score."""
    service = CandidateService(db)
    return await service.get_candidate(candidate_id)


@router.put("/{candidate_id}", response_model=CandidateDetailResponse)
async def update_candidate(
    candidate_id: int,
    data: CandidateUpdate,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Update candidate status or details."""
    service = CandidateService(db)
    result = await service.update_candidate(candidate_id, data)
    # Return full detail
    return await service.get_candidate(candidate_id)


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a candidate and their resume."""
    service = CandidateService(db)
    await service.delete_candidate(candidate_id)
    return {"message": f"Candidate #{candidate_id} deleted"}

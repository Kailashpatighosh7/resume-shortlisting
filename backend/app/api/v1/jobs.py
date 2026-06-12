"""
Job Endpoints
=============
Full CRUD for job postings.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.job_service import JobService
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """List all jobs for the current recruiter."""
    service = JobService(db)
    return await service.list_jobs(recruiter_id, page, per_page, status, search)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    data: JobCreate,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new job posting with automatic JD embedding."""
    service = JobService(db)
    return await service.create_job(recruiter_id, data)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get job details by ID."""
    service = JobService(db)
    return await service.get_job(job_id)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    data: JobUpdate,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a job posting."""
    service = JobService(db)
    return await service.update_job(job_id, data)


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a job posting and all associated data."""
    service = JobService(db)
    await service.delete_job(job_id)
    return {"message": f"Job #{job_id} deleted successfully"}

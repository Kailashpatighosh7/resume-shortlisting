"""
Job Service
===========
Business logic for job posting management.
"""

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.job import Job
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse


class JobService:
    """Manages job CRUD operations with automatic JD embedding generation."""

    def __init__(self, db: AsyncSession):
        self.repo = JobRepository(db)
        self.db = db

    async def create_job(self, recruiter_id: int, data: JobCreate) -> JobResponse:
        """Create a new job posting and compute JD embedding."""
        # Build embedding text from job fields
        embedding_text = self._build_embedding_text(data)

        # Generate embedding (lazy import to avoid startup overhead)
        try:
            from app.ai.embedding import get_embedding
            embedding = get_embedding(embedding_text)
            embedding_json = json.dumps(embedding)
        except Exception:
            embedding_json = None

        job = Job(
            recruiter_id=recruiter_id,
            title=data.title,
            department=data.department,
            required_skills=data.required_skills,
            preferred_skills=data.preferred_skills,
            min_experience=data.min_experience,
            education=data.education,
            location=data.location,
            description=data.description,
            shortlist_quota=data.shortlist_quota,
            jd_embedding=embedding_json,
        )
        job = await self.repo.create(job)
        candidate_count = await self.repo.get_candidate_count(job.id)
        return self._to_response(job, candidate_count)

    async def get_job(self, job_id: int) -> JobResponse:
        """Fetch a single job by ID."""
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")
        candidate_count = await self.repo.get_candidate_count(job.id)
        return self._to_response(job, candidate_count)

    async def list_jobs(
        self,
        recruiter_id: int,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        search: str | None = None,
    ) -> JobListResponse:
        """List jobs with pagination."""
        jobs, total = await self.repo.list_by_recruiter(
            recruiter_id, page, per_page, status, search
        )
        items = []
        for job in jobs:
            count = await self.repo.get_candidate_count(job.id)
            items.append(self._to_response(job, count))
        return JobListResponse(items=items, total=total, page=page, per_page=per_page)

    async def update_job(self, job_id: int, data: JobUpdate) -> JobResponse:
        """Update a job posting. Re-generates JD embedding if description changes."""
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(job, field, value)

        # Re-compute embedding if relevant fields changed
        if any(f in update_fields for f in ("description", "required_skills", "preferred_skills", "title")):
            try:
                from app.ai.embedding import get_embedding
                embedding_text = self._build_embedding_text_from_job(job)
                embedding = get_embedding(embedding_text)
                job.jd_embedding = json.dumps(embedding)
            except Exception:
                pass

        job = await self.repo.update(job)
        candidate_count = await self.repo.get_candidate_count(job.id)
        return self._to_response(job, candidate_count)

    async def delete_job(self, job_id: int) -> bool:
        """Delete a job and all associated data."""
        job = await self.repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")
        return await self.repo.delete(job_id)

    # ── Helpers ───────────────────────────────────────────

    @staticmethod
    def _build_embedding_text(data: JobCreate) -> str:
        """Combine job fields into a single text for embedding."""
        parts = [
            data.title,
            data.description,
            f"Required skills: {data.required_skills}",
        ]
        if data.preferred_skills:
            parts.append(f"Preferred skills: {data.preferred_skills}")
        if data.education:
            parts.append(f"Education: {data.education}")
        return " ".join(parts)

    @staticmethod
    def _build_embedding_text_from_job(job: Job) -> str:
        parts = [
            job.title or "",
            job.description or "",
            f"Required skills: {job.required_skills or ''}",
        ]
        if job.preferred_skills:
            parts.append(f"Preferred skills: {job.preferred_skills}")
        if job.education:
            parts.append(f"Education: {job.education}")
        return " ".join(parts)

    @staticmethod
    def _to_response(job: Job, candidate_count: int = 0) -> JobResponse:
        return JobResponse(
            id=job.id,
            recruiter_id=job.recruiter_id,
            title=job.title,
            department=job.department or "",
            required_skills=job.required_skills or "",
            preferred_skills=job.preferred_skills or "",
            min_experience=job.min_experience or 0,
            education=job.education or "",
            location=job.location or "",
            description=job.description,
            status=job.status,
            shortlist_quota=job.shortlist_quota or 5,
            candidate_count=candidate_count,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

"""
Candidate Service
=================
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.candidate import Candidate
from app.repositories.candidate_repo import CandidateRepository
from app.schemas.candidate import (
    CandidateUpdate, CandidateResponse, CandidateDetailResponse, CandidateListResponse,
)
from app.schemas.resume import ResumeResponse
from app.schemas.score import ScoreResponse


class CandidateService:
    """Business logic for candidate management."""

    def __init__(self, db: AsyncSession):
        self.repo = CandidateRepository(db)
        self.db = db

    async def get_candidate(self, candidate_id: int) -> CandidateDetailResponse:
        """Get candidate with resume and score details."""
        candidate = await self.repo.get_with_details(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate #{candidate_id} not found")

        resume_data = None
        if candidate.resume:
            resume_data = ResumeResponse.model_validate(candidate.resume)

        score_data = None
        if candidate.scores:
            # Get the latest score
            latest = sorted(candidate.scores, key=lambda s: s.scored_at, reverse=True)[0]
            score_data = ScoreResponse.model_validate(latest)

        return CandidateDetailResponse(
            id=candidate.id,
            job_id=candidate.job_id,
            name=candidate.name,
            email=candidate.email or "",
            phone=candidate.phone or "",
            status=candidate.status,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            resume=resume_data,
            score=score_data,
        )

    async def list_candidates_by_job(
        self,
        job_id: int,
        page: int = 1,
        per_page: int = 50,
        status: str | None = None,
        search: str | None = None,
    ) -> CandidateListResponse:
        candidates, total = await self.repo.list_by_job(
            job_id, page, per_page, status, search
        )
        items = [CandidateResponse.model_validate(c) for c in candidates]
        return CandidateListResponse(items=items, total=total, page=page, per_page=per_page)

    async def list_all_candidates(
        self,
        page: int = 1,
        per_page: int = 50,
        search: str | None = None,
    ) -> CandidateListResponse:
        candidates, total = await self.repo.list_all(page, per_page, search)
        items = [CandidateResponse.model_validate(c) for c in candidates]
        return CandidateListResponse(items=items, total=total, page=page, per_page=per_page)

    async def update_candidate(
        self, candidate_id: int, data: CandidateUpdate
    ) -> CandidateResponse:
        candidate = await self.repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate #{candidate_id} not found")

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(candidate, field, value)

        candidate = await self.repo.update(candidate)
        return CandidateResponse.model_validate(candidate)

    async def delete_candidate(self, candidate_id: int) -> bool:
        candidate = await self.repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate #{candidate_id} not found")
        return await self.repo.delete(candidate_id)

"""
Interview Service
=================
Business logic for interview scheduling and management.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.interview import Interview
from app.repositories.interview_repo import InterviewRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.job_repo import JobRepository
from app.schemas.interview import (
    InterviewCreate, InterviewUpdate, InterviewResponse, InterviewListResponse,
)


class InterviewService:
    """Manages interview scheduling with automatic email triggers."""

    def __init__(self, db: AsyncSession):
        self.repo = InterviewRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.job_repo = JobRepository(db)
        self.db = db

    async def create_interview(
        self, recruiter_id: int, data: InterviewCreate
    ) -> InterviewResponse:
        """Schedule a new interview and send notification email."""
        # Validate candidate and job exist
        candidate = await self.candidate_repo.get_by_id(data.candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate #{data.candidate_id} not found")

        job = await self.job_repo.get_by_id(data.job_id)
        if not job:
            raise NotFoundException(f"Job #{data.job_id} not found")

        interview = Interview(
            candidate_id=data.candidate_id,
            job_id=data.job_id,
            recruiter_id=recruiter_id,
            scheduled_at=data.scheduled_at,
            mode=data.mode,
            meeting_link=data.meeting_link,
            notes=data.notes,
            status="scheduled",
        )
        interview = await self.repo.create(interview)

        # Update candidate status
        candidate.status = "interview"
        await self.candidate_repo.update(candidate)

        # Send interview email notification
        try:
            from app.services.email_service import EmailService
            email_svc = EmailService(self.db)
            await email_svc.send_interview_notification(
                candidate_id=data.candidate_id,
                job_id=data.job_id,
                interview_date=data.scheduled_at.strftime("%B %d, %Y"),
                interview_time=data.scheduled_at.strftime("%I:%M %p"),
                mode=data.mode,
                meeting_link=data.meeting_link,
            )
        except Exception as e:
            print(f"⚠️ Interview email failed: {e}")

        return self._to_response(interview, candidate.name, job.title)

    async def list_interviews(
        self,
        recruiter_id: int | None = None,
        status: str | None = None,
    ) -> InterviewListResponse:
        """List interviews with optional filtering."""
        if recruiter_id:
            interviews = await self.repo.list_by_recruiter(recruiter_id, status)
        else:
            interviews = await self.repo.list_all(status)

        items = []
        for iv in interviews:
            candidate = await self.candidate_repo.get_by_id(iv.candidate_id)
            job = await self.job_repo.get_by_id(iv.job_id)
            items.append(self._to_response(
                iv,
                candidate.name if candidate else "",
                job.title if job else "",
            ))

        return InterviewListResponse(items=items, total=len(items))

    async def update_interview(
        self, interview_id: int, data: InterviewUpdate
    ) -> InterviewResponse:
        """Update interview details."""
        interview = await self.repo.get_by_id(interview_id)
        if not interview:
            raise NotFoundException(f"Interview #{interview_id} not found")

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(interview, field, value)

        interview = await self.repo.update(interview)
        candidate = await self.candidate_repo.get_by_id(interview.candidate_id)
        job = await self.job_repo.get_by_id(interview.job_id)

        return self._to_response(
            interview,
            candidate.name if candidate else "",
            job.title if job else "",
        )

    async def delete_interview(self, interview_id: int) -> bool:
        """Cancel/delete an interview."""
        interview = await self.repo.get_by_id(interview_id)
        if not interview:
            raise NotFoundException(f"Interview #{interview_id} not found")
        return await self.repo.delete(interview_id)

    @staticmethod
    def _to_response(
        interview: Interview, candidate_name: str, job_title: str
    ) -> InterviewResponse:
        return InterviewResponse(
            id=interview.id,
            candidate_id=interview.candidate_id,
            job_id=interview.job_id,
            recruiter_id=interview.recruiter_id,
            scheduled_at=interview.scheduled_at,
            mode=interview.mode,
            meeting_link=interview.meeting_link or "",
            status=interview.status,
            notes=interview.notes or "",
            candidate_name=candidate_name,
            job_title=job_title,
            created_at=interview.created_at,
            updated_at=interview.updated_at,
        )

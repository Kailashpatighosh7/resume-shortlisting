"""
Email Service
=============
Business logic for sending and logging emails.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.email_sent import EmailSent
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.job_repo import JobRepository
from app.repositories.email_repo import EmailRepository
from app.emails.smtp import send_email
from app.emails.templates import (
    shortlisted_template,
    rejected_template,
    interview_scheduled_template,
)
from app.schemas.email import EmailLogResponse, EmailLogListResponse, EmailStatsResponse


class EmailService:
    """Manages email sending and logging."""

    def __init__(self, db: AsyncSession):
        self.email_repo = EmailRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.job_repo = JobRepository(db)
        self.db = db

    async def send_notification(
        self,
        candidate_id: int,
        job_id: int,
        email_type: str,
        custom_subject: str | None = None,
        custom_body: str | None = None,
    ) -> EmailLogResponse:
        """
        Send a notification email and log it.

        email_type: 'shortlisted', 'rejected', 'interview_scheduled', 'custom'
        """
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate #{candidate_id} not found")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")

        if not candidate.email:
            raise NotFoundException("Candidate has no email address")

        # Generate subject and body from template
        if email_type == "shortlisted":
            subject, body = shortlisted_template(candidate.name, job.title)
        elif email_type == "rejected":
            subject, body = rejected_template(candidate.name, job.title)
        elif email_type == "custom":
            subject = custom_subject or f"Update regarding {job.title}"
            body = custom_body or ""
        else:
            subject = custom_subject or f"Update regarding {job.title}"
            body = custom_body or ""

        # Override with custom values if provided
        if custom_subject:
            subject = custom_subject
        if custom_body:
            body = custom_body

        # Send email
        success = send_email(candidate.email, subject, body)

        # Log email
        email_log = EmailSent(
            candidate_id=candidate_id,
            job_id=job_id,
            email_type=email_type,
            recipient_email=candidate.email,
            subject=subject,
            body=body,
            status="sent" if success else "failed",
        )
        email_log = await self.email_repo.create(email_log)
        return EmailLogResponse.model_validate(email_log)

    async def send_interview_notification(
        self,
        candidate_id: int,
        job_id: int,
        interview_date: str,
        interview_time: str,
        mode: str,
        meeting_link: str = "",
    ) -> EmailLogResponse:
        """Send an interview scheduled notification."""
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate #{candidate_id} not found")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")

        if not candidate.email:
            raise NotFoundException("Candidate has no email address")

        subject, body = interview_scheduled_template(
            candidate.name, job.title,
            interview_date, interview_time,
            mode, meeting_link,
        )

        success = send_email(candidate.email, subject, body)

        email_log = EmailSent(
            candidate_id=candidate_id,
            job_id=job_id,
            email_type="interview_scheduled",
            recipient_email=candidate.email,
            subject=subject,
            body=body,
            status="sent" if success else "failed",
        )
        email_log = await self.email_repo.create(email_log)
        return EmailLogResponse.model_validate(email_log)

    async def list_emails(
        self,
        email_type: str | None = None,
        job_id: int | None = None,
        limit: int = 100,
    ) -> EmailLogListResponse:
        """List email logs."""
        emails = await self.email_repo.list_all(email_type, job_id, limit)
        items = [EmailLogResponse.model_validate(e) for e in emails]
        total = await self.email_repo.count_all()
        return EmailLogListResponse(items=items, total=total)

    async def get_stats(self) -> EmailStatsResponse:
        """Get aggregated email sending statistics."""
        return EmailStatsResponse(
            total=await self.email_repo.count_all(),
            sent=await self.email_repo.count_by_status("sent"),
            failed=await self.email_repo.count_by_status("failed"),
            shortlisted=await self.email_repo.count_by_type("shortlisted"),
            rejected=await self.email_repo.count_by_type("rejected"),
            interview_scheduled=await self.email_repo.count_by_type("interview_scheduled"),
            custom=await self.email_repo.count_by_type("custom"),
        )

"""
Candidate Schemas
=================
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CandidateCreate(BaseModel):
    """Create candidate (usually auto-created during resume upload)."""
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=50)


class CandidateUpdate(BaseModel):
    """Update candidate details."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(new|shortlisted|rejected|interview|hired)$")


class CandidateResponse(BaseModel):
    """Candidate response."""
    id: int
    job_id: int
    name: str
    email: str
    phone: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateDetailResponse(CandidateResponse):
    """Candidate with resume and score data."""
    resume: Optional["ResumeResponse"] = None
    score: Optional["ScoreResponse"] = None


class CandidateListResponse(BaseModel):
    """Paginated candidate list."""
    items: List[CandidateResponse]
    total: int
    page: int
    per_page: int


# Forward reference imports
from app.schemas.resume import ResumeResponse  # noqa: E402
from app.schemas.score import ScoreResponse  # noqa: E402

CandidateDetailResponse.model_rebuild()

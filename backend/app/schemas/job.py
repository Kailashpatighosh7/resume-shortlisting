"""
Job Schemas
===========
Request / response models for job endpoints.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    """Create a new job posting."""
    title: str = Field(..., min_length=1, max_length=255)
    department: str = Field(default="", max_length=255)
    required_skills: str = Field(..., description="Comma-separated required skills")
    preferred_skills: str = Field(default="", description="Comma-separated preferred skills")
    min_experience: int = Field(default=0, ge=0)
    education: str = Field(default="", max_length=255)
    location: str = Field(default="", max_length=255)
    description: str = Field(..., min_length=10)
    shortlist_quota: int = Field(default=5, ge=1, le=100, description="Number of top candidates to auto-shortlist")


class JobUpdate(BaseModel):
    """Update an existing job posting."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    department: Optional[str] = None
    required_skills: Optional[str] = None
    preferred_skills: Optional[str] = None
    min_experience: Optional[int] = Field(None, ge=0)
    education: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(open|closed|draft)$")
    shortlist_quota: Optional[int] = Field(None, ge=1, le=100)


class JobResponse(BaseModel):
    """Job listing response."""
    id: int
    recruiter_id: int
    title: str
    department: str
    required_skills: str
    preferred_skills: str
    min_experience: int
    education: str
    location: str
    description: str
    status: str
    shortlist_quota: int = 5
    candidate_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Paginated job list."""
    items: List[JobResponse]
    total: int
    page: int
    per_page: int

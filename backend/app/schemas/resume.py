"""
Resume Schemas
==============
"""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    """Resume metadata response."""
    id: int
    candidate_id: int
    original_filename: str
    file_path: str
    parsed_text: str = ""
    parsed_data: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeUploadResponse(BaseModel):
    """Response after uploading one or more resumes."""
    uploaded: int
    candidates_created: int
    message: str


class ZipUploadResponse(BaseModel):
    """Response after processing a ZIP archive of resumes."""
    total_files: int
    processed: int
    failed: int
    candidates_created: int
    message: str


class ParsedResumeData(BaseModel):
    """Structured data extracted from a resume."""
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = []
    education: list[str] = []
    experience: list[str] = []
    projects: list[str] = []

"""
Resume Endpoints
================
Upload, download, and manage resumes.
Supports individual file uploads and bulk ZIP archive uploads.
"""

import os
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.core.exceptions import FileProcessingException
from app.core.supabase_storage import download_file
from app.services.resume_service import ResumeService, MIME_TYPES
from app.schemas.resume import ResumeUploadResponse, ZipUploadResponse, ResumeResponse

router = APIRouter()


@router.post("/upload/{job_id}", response_model=ResumeUploadResponse, status_code=201)
async def upload_resumes(
    job_id: int,
    files: List[UploadFile] = File(...),
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload one or more resumes for a specific job."""
    service = ResumeService(db)
    return await service.upload_resumes(job_id, files)


@router.post("/upload-zip/{job_id}", response_model=ZipUploadResponse, status_code=201)
async def upload_zip(
    job_id: int,
    file: UploadFile = File(...),
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a ZIP archive containing multiple resumes for a specific job.

    The ZIP may contain PDF and DOCX files in any directory structure.
    Unsupported file types are silently skipped.
    Processing errors for one file do not stop processing of other files.
    """
    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext != ".zip":
        raise FileProcessingException(
            "Only .zip files are accepted. Please upload a ZIP archive."
        )

    service = ResumeService(db)
    return await service.upload_zip(job_id, file)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get resume metadata."""
    service = ResumeService(db)
    return await service.get_resume(resume_id)


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Download the original resume file from Supabase Storage."""
    service = ResumeService(db)
    resume = await service.get_resume(resume_id)

    # Download file bytes from Supabase Storage
    file_bytes = download_file(resume.file_path)

    # Determine content type from the original filename
    ext = os.path.splitext(resume.original_filename)[1].lower()
    content_type = MIME_TYPES.get(ext, "application/octet-stream")

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{resume.original_filename}"',
        },
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a resume and its file."""
    service = ResumeService(db)
    await service.delete_resume(resume_id)
    return {"message": f"Resume #{resume_id} deleted"}

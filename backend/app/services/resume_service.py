"""
Resume Service
==============
Handles resume upload, file storage, parsing, and embedding generation.
Supports both individual file uploads and bulk ZIP archive uploads.

Files are stored in Supabase Storage.  Text extraction still uses
local temp files (pdfplumber / python-docx require filesystem paths)
which are cleaned up immediately after use.
"""

import json
import uuid
import zipfile
import logging
import tempfile
import os
from typing import List

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import FileProcessingException, NotFoundException
from app.core.supabase_storage import upload_file, delete_file
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.resume_repo import ResumeRepository
from app.utils.file_parser import extract_text
from app.utils.resume_parser import parse_resume_text
from app.schemas.resume import ResumeUploadResponse, ZipUploadResponse, ResumeResponse


logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}

# MIME types for common resume formats
MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
}


class ResumeService:
    """Manages resume upload, parsing, and storage."""

    def __init__(self, db: AsyncSession):
        self.resume_repo = ResumeRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.db = db

    # ── Shared Single-Resume Pipeline ─────────────────────────

    async def _process_single_resume(
        self,
        job_id: int,
        file_bytes: bytes,
        original_filename: str,
    ) -> bool:
        """
        Process a single resume from raw bytes.

        Pipeline: write to temp file → extract text → parse structured data
                  → generate embedding → upload to Supabase Storage
                  → create Candidate → create Resume record.

        Args:
            job_id: The job this resume belongs to.
            file_bytes: Raw file content.
            original_filename: The original name of the uploaded file.

        Returns:
            True if processing succeeded, False otherwise.
        """
        ext = os.path.splitext(original_filename)[1].lower()
        storage_path = None

        try:
            # Write to temp file for text extraction (pdfplumber/docx need paths)
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            try:
                # Extract text
                parsed_text = extract_text(tmp_path)
            finally:
                # Always clean up temp file
                os.unlink(tmp_path)

            # Parse structured data
            parsed_data = parse_resume_text(parsed_text)

            # Generate embedding
            try:
                from app.ai.embedding import get_embedding
                embedding = get_embedding(parsed_text)
                embedding_json = json.dumps(embedding)
            except Exception:
                embedding_json = None

            # Upload to Supabase Storage with a unique path
            unique_name = f"{uuid.uuid4().hex}{ext}"
            storage_path = f"job_{job_id}/{unique_name}"
            content_type = MIME_TYPES.get(ext, "application/octet-stream")

            upload_file(
                path=storage_path,
                file_bytes=file_bytes,
                content_type=content_type,
            )

            # Create candidate
            candidate = Candidate(
                job_id=job_id,
                name=parsed_data.name or original_filename,
                email=parsed_data.email or "",
                phone=parsed_data.phone or "",
                status="new",
            )
            candidate = await self.candidate_repo.create(candidate)

            # Create resume record (file_path stores the Supabase storage path)
            resume = Resume(
                candidate_id=candidate.id,
                original_filename=original_filename,
                file_path=storage_path,
                parsed_text=parsed_text,
                parsed_data=parsed_data.model_dump(),
                resume_embedding=embedding_json,
            )
            await self.resume_repo.create(resume)
            return True

        except Exception as e:
            logger.error(f"Failed to process resume '{original_filename}': {e}")
            # Clean up Supabase file on error
            if storage_path:
                try:
                    delete_file(storage_path)
                except Exception:
                    pass
            return False

    # ── Individual File Upload ────────────────────────────────

    async def upload_resumes(
        self,
        job_id: int,
        files: List[UploadFile],
    ) -> ResumeUploadResponse:
        """
        Upload one or more resumes for a job.

        For each file:
        1. Validate file type
        2. Read bytes
        3. Extract text (via temp file)
        4. Parse structured data
        5. Generate embedding
        6. Upload to Supabase Storage
        7. Create candidate + resume records
        """
        uploaded = 0
        candidates_created = 0

        for file in files:
            # Validate extension
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue

            # Validate file size
            contents = await file.read()
            if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                continue

            success = await self._process_single_resume(
                job_id, contents, file.filename
            )
            if success:
                uploaded += 1
                candidates_created += 1

        return ResumeUploadResponse(
            uploaded=uploaded,
            candidates_created=candidates_created,
            message=f"Successfully processed {uploaded} resume(s)",
        )

    # ── ZIP Archive Upload ────────────────────────────────────

    async def upload_zip(
        self,
        job_id: int,
        zip_file: UploadFile,
    ) -> ZipUploadResponse:
        """
        Upload and process a ZIP archive containing multiple resumes.

        Steps:
        1. Validate ZIP size
        2. Save to system temp file
        3. Open and validate the archive
        4. Prevent ZIP Slip / path traversal
        5. Read each file as bytes and process
        6. Return statistics
        """
        # ── Read & validate size ──
        contents = await zip_file.read()
        max_zip_bytes = settings.MAX_ZIP_SIZE_MB * 1024 * 1024

        if len(contents) > max_zip_bytes:
            raise FileProcessingException(
                f"ZIP file exceeds maximum size of {settings.MAX_ZIP_SIZE_MB}MB"
            )

        if len(contents) == 0:
            raise FileProcessingException("Uploaded file is empty")

        # ── Save to system temp file (auto-cleaned) ──
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp.write(contents)
            temp_zip_path = tmp.name

        try:
            return await self._extract_and_process_zip(job_id, temp_zip_path)
        finally:
            # Always clean up temp ZIP
            if os.path.exists(temp_zip_path):
                os.unlink(temp_zip_path)

    async def _extract_and_process_zip(
        self,
        job_id: int,
        zip_path: str,
    ) -> ZipUploadResponse:
        """Extract files from a ZIP and process each resume."""

        # ── Open & validate ──
        try:
            zf = zipfile.ZipFile(zip_path, "r")
        except zipfile.BadZipFile:
            raise FileProcessingException("Invalid or corrupted ZIP file")

        with zf:
            # ── Collect supported file entries ──
            entries = []
            for info in zf.infolist():
                # Skip directories
                if info.is_dir():
                    continue

                # Skip macOS metadata
                filename = info.filename
                if "__MACOSX" in filename or filename.startswith("."):
                    continue

                # ── ZIP Slip prevention ──
                # Reject entries with path traversal components
                normalized = os.path.normpath(filename)
                if normalized.startswith("..") or os.path.isabs(normalized):
                    logger.warning(f"Skipping suspicious ZIP entry: {filename}")
                    continue

                entries.append(info)

            total_files = len(entries)

            # ── File count limit ──
            if total_files > settings.MAX_ZIP_FILE_COUNT:
                raise FileProcessingException(
                    f"ZIP contains {total_files} files, exceeding the "
                    f"maximum of {settings.MAX_ZIP_FILE_COUNT}"
                )

            processed = 0
            failed = 0
            candidates_created = 0

            for info in entries:
                # Get just the filename, ignoring any subdirectory structure
                original_name = os.path.basename(info.filename)
                ext = os.path.splitext(original_name)[1].lower()

                # Skip unsupported extensions
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                # Validate individual file size
                if info.file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                    logger.warning(
                        f"Skipping oversized file in ZIP: {original_name} "
                        f"({info.file_size} bytes)"
                    )
                    failed += 1
                    continue

                # ── Read file bytes from ZIP ──
                try:
                    file_bytes = zf.read(info)
                except Exception as e:
                    logger.error(f"Failed to read '{original_name}' from ZIP: {e}")
                    failed += 1
                    continue

                # ── Process resume ──
                success = await self._process_single_resume(
                    job_id, file_bytes, original_name
                )
                if success:
                    processed += 1
                    candidates_created += 1
                else:
                    failed += 1

        return ZipUploadResponse(
            total_files=total_files,
            processed=processed,
            failed=failed,
            candidates_created=candidates_created,
            message=(
                f"ZIP processed successfully: {processed} resume(s) processed, "
                f"{failed} failed out of {total_files} total files"
            ),
        )

    # ── Read / Delete ─────────────────────────────────────────

    async def get_resume(self, resume_id: int) -> ResumeResponse:
        """Get resume details."""
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume:
            raise NotFoundException(f"Resume #{resume_id} not found")
        return ResumeResponse.model_validate(resume)

    async def get_resume_by_candidate(self, candidate_id: int) -> ResumeResponse:
        """Get resume by candidate ID."""
        resume = await self.resume_repo.get_by_candidate_id(candidate_id)
        if not resume:
            raise NotFoundException(f"No resume found for candidate #{candidate_id}")
        return ResumeResponse.model_validate(resume)

    async def delete_resume(self, resume_id: int) -> bool:
        """Delete a resume and its file from Supabase Storage."""
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume:
            raise NotFoundException(f"Resume #{resume_id} not found")

        # Delete file from Supabase Storage
        if resume.file_path:
            try:
                delete_file(resume.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete storage file '{resume.file_path}': {e}")

        return await self.resume_repo.delete(resume_id)

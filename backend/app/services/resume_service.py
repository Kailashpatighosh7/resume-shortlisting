"""
Resume Service
==============
Handles resume upload, file storage, parsing, and embedding generation.
Supports both individual file uploads and bulk ZIP archive uploads.
"""

import os
import json
import uuid
import zipfile
import logging
from typing import List, Tuple

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import FileProcessingException, NotFoundException
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.resume_repo import ResumeRepository
from app.utils.file_parser import extract_text
from app.utils.resume_parser import parse_resume_text
from app.schemas.resume import ResumeUploadResponse, ZipUploadResponse, ResumeResponse


logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}


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
        file_path: str,
        original_filename: str,
    ) -> bool:
        """
        Process a single resume file that already exists on disk.

        Pipeline: extract text → parse structured data → generate embedding
                  → create Candidate → create Resume record.

        Args:
            job_id: The job this resume belongs to.
            file_path: Absolute path to the saved file on disk.
            original_filename: The original name of the uploaded file.

        Returns:
            True if processing succeeded, False otherwise.
        """
        try:
            # Extract text
            parsed_text = extract_text(file_path)

            # Parse structured data
            parsed_data = parse_resume_text(parsed_text)

            # Generate embedding
            try:
                from app.ai.embedding import get_embedding
                embedding = get_embedding(parsed_text)
                embedding_json = json.dumps(embedding)
            except Exception:
                embedding_json = None

            # Create candidate
            candidate = Candidate(
                job_id=job_id,
                name=parsed_data.name or original_filename,
                email=parsed_data.email or "",
                phone=parsed_data.phone or "",
                status="new",
            )
            candidate = await self.candidate_repo.create(candidate)

            # Create resume record
            resume = Resume(
                candidate_id=candidate.id,
                original_filename=original_filename,
                file_path=file_path,
                parsed_text=parsed_text,
                parsed_data=parsed_data.model_dump(),
                resume_embedding=embedding_json,
            )
            await self.resume_repo.create(resume)
            return True

        except Exception as e:
            logger.error(f"Failed to process resume '{original_filename}': {e}")
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
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
        2. Save to disk
        3. Extract text
        4. Parse structured data
        5. Generate embedding
        6. Create candidate + resume records
        """
        uploaded = 0
        candidates_created = 0

        # Job-specific upload directory
        job_dir = os.path.join(settings.UPLOAD_DIR, "resumes", f"job_{job_id}")
        os.makedirs(job_dir, exist_ok=True)

        for file in files:
            # Validate extension
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue

            # Validate file size
            contents = await file.read()
            if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                continue

            # Save file to disk with original filename
            safe_name = os.path.basename(file.filename)
            file_path = self._resolve_unique_path(job_dir, safe_name)

            with open(file_path, "wb") as f:
                f.write(contents)

            success = await self._process_single_resume(
                job_id, file_path, file.filename
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
        2. Save to temp location
        3. Open and validate the archive
        4. Prevent ZIP Slip / path traversal
        5. Extract supported files to job-specific directory
        6. Process each resume independently (errors don't halt others)
        7. Return statistics
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

        # ── Save temp ZIP ──
        temp_dir = os.path.join(settings.UPLOAD_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_zip_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.zip")

        with open(temp_zip_path, "wb") as f:
            f.write(contents)

        try:
            return await self._extract_and_process_zip(job_id, temp_zip_path)
        finally:
            # Always clean up temp ZIP
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

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

            # ── Prepare job directory ──
            job_dir = os.path.join(
                settings.UPLOAD_DIR, "resumes", f"job_{job_id}"
            )
            os.makedirs(job_dir, exist_ok=True)

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

                # ── Extract to disk ──
                file_path = self._resolve_unique_path(job_dir, original_name)
                try:
                    with zf.open(info) as src, open(file_path, "wb") as dst:
                        dst.write(src.read())
                except Exception as e:
                    logger.error(f"Failed to extract '{original_name}': {e}")
                    failed += 1
                    continue

                # ── Process resume ──
                success = await self._process_single_resume(
                    job_id, file_path, original_name
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

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _resolve_unique_path(directory: str, filename: str) -> str:
        """
        Resolve a unique file path in the given directory.

        If `filename` already exists, appends _1, _2, etc. before the
        extension to avoid overwriting.

        Args:
            directory: Target directory path.
            filename: Desired filename.

        Returns:
            Full path that does not collide with existing files.
        """
        name, ext = os.path.splitext(filename)
        candidate_path = os.path.join(directory, filename)
        counter = 1
        while os.path.exists(candidate_path):
            candidate_path = os.path.join(directory, f"{name}_{counter}{ext}")
            counter += 1
        return candidate_path

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
        """Delete a resume and its file."""
        resume = await self.resume_repo.get_by_id(resume_id)
        if not resume:
            raise NotFoundException(f"Resume #{resume_id} not found")

        # Delete file
        if resume.file_path and os.path.exists(resume.file_path):
            os.remove(resume.file_path)

        return await self.resume_repo.delete(resume_id)

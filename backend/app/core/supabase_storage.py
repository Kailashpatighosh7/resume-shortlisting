"""
Supabase Storage Utility
========================
Wraps the Supabase Storage API for file upload, download, and deletion.
Uses a lazy-initialised client singleton so the connection is created
only once and reused across requests.
"""

import logging
from typing import Optional

from supabase import create_client, Client

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Lazy Singleton ────────────────────────────────────────────

_client: Optional[Client] = None


def _get_client() -> Client:
    """Return a cached Supabase client (created on first call)."""
    global _client
    if _client is None:
        _client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _client


# ── Public API ────────────────────────────────────────────────


def upload_file(
    path: str,
    file_bytes: bytes,
    content_type: str = "application/octet-stream",
    bucket: Optional[str] = None,
) -> str:
    """
    Upload a file to Supabase Storage.

    Args:
        path: Object path inside the bucket (e.g. ``job_5/abc123.pdf``).
        file_bytes: Raw file content.
        content_type: MIME type of the file.
        bucket: Bucket name (defaults to ``settings.SUPABASE_STORAGE_BUCKET``).

    Returns:
        The storage path that was written (same as *path*).
    """
    bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
    client = _get_client()

    client.storage.from_(bucket).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": content_type},
    )
    logger.info("Uploaded %s to bucket '%s'", path, bucket)
    return path


def download_file(
    path: str,
    bucket: Optional[str] = None,
) -> bytes:
    """
    Download a file from Supabase Storage.

    Args:
        path: Object path inside the bucket.
        bucket: Bucket name (defaults to ``settings.SUPABASE_STORAGE_BUCKET``).

    Returns:
        The raw file bytes.
    """
    bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
    client = _get_client()

    data = client.storage.from_(bucket).download(path)
    return data


def delete_file(
    path: str,
    bucket: Optional[str] = None,
) -> None:
    """
    Delete a file from Supabase Storage.

    Args:
        path: Object path inside the bucket.
        bucket: Bucket name (defaults to ``settings.SUPABASE_STORAGE_BUCKET``).
    """
    bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
    client = _get_client()

    client.storage.from_(bucket).remove([path])
    logger.info("Deleted %s from bucket '%s'", path, bucket)


def get_signed_url(
    path: str,
    expires_in: int = 3600,
    bucket: Optional[str] = None,
) -> str:
    """
    Generate a temporary signed URL for a private file.

    Args:
        path: Object path inside the bucket.
        expires_in: URL validity in seconds (default 1 hour).
        bucket: Bucket name (defaults to ``settings.SUPABASE_STORAGE_BUCKET``).

    Returns:
        A signed URL string.
    """
    bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
    client = _get_client()

    result = client.storage.from_(bucket).create_signed_url(path, expires_in)
    return result["signedURL"]

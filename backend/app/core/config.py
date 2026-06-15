"""
Application Configuration
=========================
Centralised settings management using pydantic-settings.
All values are loaded from environment variables / .env file.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "AI Resume Screening System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_screening"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://postgres:postgres@localhost:5432/resume_screening"

    # ── JWT ──────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["https://resumeshortlisst.netlify.app", "http://localhost:3000"]

    # ── Supabase Storage ──────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "resumes"

    # ── File Upload (validation limits) ──────────────────────
    MAX_FILE_SIZE_MB: int = 10
    MAX_ZIP_SIZE_MB: int = 200
    MAX_ZIP_FILE_COUNT: int = 500

    # ── Email (SMTP) ─────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "AI Resume Screening"
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True

    # ── AI Model ─────────────────────────────────────────────
    AI_MODEL_NAME: str = "all-MiniLM-L6-v2"


# Singleton instance — import this everywhere
settings = Settings()

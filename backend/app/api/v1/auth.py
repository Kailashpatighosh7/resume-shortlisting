"""
Auth Endpoints
==============
POST /auth/register                — Register a new recruiter
POST /auth/login                   — Login and receive JWT token
GET  /auth/me                      — Get current user profile
PUT  /auth/me                      — Update profile
POST /auth/password                — Change password
POST /auth/forgot-password/verify  — Verify email for password reset
POST /auth/forgot-password/reset   — Reset password
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest, TokenResponse,
    RecruiterResponse, RecruiterUpdate, PasswordChange,
    ForgotPasswordVerify, ForgotPasswordReset,
)

router = APIRouter()


@router.post("/register", response_model=RecruiterResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new recruiter account."""
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login and receive a JWT access token.

    Accepts OAuth2-compliant form data. The ``username`` field is
    treated as the recruiter's email address.
    """
    service = AuthService(db)
    return await service.login_with_credentials(form_data.username, form_data.password)


@router.get("/me", response_model=RecruiterResponse)
async def get_me(
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get the currently authenticated recruiter's profile."""
    service = AuthService(db)
    return await service.get_current_user(recruiter_id)


@router.put("/me", response_model=RecruiterResponse)
async def update_me(
    data: RecruiterUpdate,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Update the current recruiter's profile."""
    service = AuthService(db)
    return await service.update_profile(recruiter_id, data.full_name, data.company)


@router.post("/password")
async def change_password(
    data: PasswordChange,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Change the current recruiter's password."""
    service = AuthService(db)
    await service.change_password(recruiter_id, data.current_password, data.new_password)
    return {"message": "Password changed successfully"}


@router.post("/forgot-password/verify")
async def forgot_password_verify(
    data: ForgotPasswordVerify,
    db: AsyncSession = Depends(get_db),
):
    """Verify that a recruiter email exists for password reset."""
    service = AuthService(db)
    await service.verify_email(data.email)
    return {"message": "Email verified", "email": data.email}


@router.post("/forgot-password/reset")
async def forgot_password_reset(
    data: ForgotPasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """Reset password for a verified recruiter email."""
    service = AuthService(db)
    await service.reset_password(data.email, data.new_password)
    return {"message": "Password has been reset successfully"}

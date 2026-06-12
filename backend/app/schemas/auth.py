"""
Auth Schemas
============
Request / response models for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Recruiter registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(default="", max_length=255)


class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class RecruiterResponse(BaseModel):
    """Public recruiter profile."""
    id: int
    email: str
    full_name: str
    company: str

    model_config = {"from_attributes": True}


class RecruiterUpdate(BaseModel):
    """Profile update request."""
    full_name: str | None = None
    company: str | None = None


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordVerify(BaseModel):
    """Verify email exists for password reset."""
    email: EmailStr


class ForgotPasswordReset(BaseModel):
    """Reset password after email verification."""
    email: EmailStr
    new_password: str = Field(..., min_length=8, max_length=128)

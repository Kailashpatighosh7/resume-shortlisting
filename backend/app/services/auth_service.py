"""
Auth Service
=============
Business logic for recruiter authentication.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException
from app.models.recruiter import Recruiter
from app.repositories.recruiter_repo import RecruiterRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RecruiterResponse


class AuthService:
    """Handles recruiter registration, login, and profile management."""

    def __init__(self, db: AsyncSession):
        self.repo = RecruiterRepository(db)
        self.db = db

    async def register(self, data: RegisterRequest) -> RecruiterResponse:
        """
        Register a new recruiter.

        Raises:
            ConflictException: If email already exists.
        """
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictException("A recruiter with this email already exists")

        recruiter = Recruiter(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            company=data.company,
        )
        recruiter = await self.repo.create(recruiter)
        return RecruiterResponse.model_validate(recruiter)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """
        Authenticate a recruiter and return a JWT token.

        Raises:
            UnauthorizedException: If credentials are invalid.
        """
        return await self.login_with_credentials(data.email, data.password)

    async def login_with_credentials(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate a recruiter by email and password strings.

        This is the shared implementation used by both the OAuth2 form-based
        login endpoint and the JSON-based LoginRequest path.

        Raises:
            UnauthorizedException: If credentials are invalid.
        """
        recruiter = await self.repo.get_by_email(email)
        if not recruiter or not verify_password(password, recruiter.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        token = create_access_token(data={"sub": str(recruiter.id)})
        return TokenResponse(access_token=token)

    async def get_current_user(self, recruiter_id: int) -> RecruiterResponse:
        """Retrieve the currently authenticated recruiter's profile."""
        recruiter = await self.repo.get_by_id(recruiter_id)
        if not recruiter:
            raise NotFoundException("Recruiter not found")
        return RecruiterResponse.model_validate(recruiter)

    async def update_profile(
        self, recruiter_id: int, full_name: str | None = None, company: str | None = None
    ) -> RecruiterResponse:
        """Update recruiter profile fields."""
        recruiter = await self.repo.get_by_id(recruiter_id)
        if not recruiter:
            raise NotFoundException("Recruiter not found")

        if full_name is not None:
            recruiter.full_name = full_name
        if company is not None:
            recruiter.company = company

        recruiter = await self.repo.update(recruiter)
        return RecruiterResponse.model_validate(recruiter)

    async def change_password(
        self, recruiter_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change the recruiter's password after verifying the current one."""
        recruiter = await self.repo.get_by_id(recruiter_id)
        if not recruiter:
            raise NotFoundException("Recruiter not found")

        if not verify_password(current_password, recruiter.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        recruiter.hashed_password = hash_password(new_password)
        await self.repo.update(recruiter)
        return True

    async def verify_email(self, email: str) -> bool:
        """
        Verify that a recruiter with the given email exists.

        Raises:
            NotFoundException: If no recruiter has this email.
        """
        recruiter = await self.repo.get_by_email(email)
        if not recruiter:
            raise NotFoundException("No account found with this email address")
        return True

    async def reset_password(self, email: str, new_password: str) -> bool:
        """
        Reset a recruiter's password (forgot password flow).

        The caller must have already verified the email exists.

        Raises:
            NotFoundException: If no recruiter has this email.
        """
        recruiter = await self.repo.get_by_email(email)
        if not recruiter:
            raise NotFoundException("No account found with this email address")

        recruiter.hashed_password = hash_password(new_password)
        await self.repo.update(recruiter)
        return True

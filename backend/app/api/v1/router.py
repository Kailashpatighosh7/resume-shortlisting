"""
API v1 Router
=============
Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.rankings import router as rankings_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1.emails import router as emails_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(candidates_router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(rankings_router, prefix="", tags=["Rankings"])
api_router.include_router(interviews_router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(emails_router, prefix="/emails", tags=["Emails"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

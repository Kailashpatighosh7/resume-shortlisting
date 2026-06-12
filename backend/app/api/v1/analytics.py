"""
Analytics Endpoints
===================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsDashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_dashboard(
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get full analytics dashboard data."""
    service = AnalyticsService(db)
    return await service.get_dashboard(recruiter_id)

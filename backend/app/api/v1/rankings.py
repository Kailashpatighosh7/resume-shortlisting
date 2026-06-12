"""
Ranking Endpoints
=================
Trigger ranking, get results, explainability, CSV export.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database.session import get_db
from app.api.deps import get_current_recruiter_id
from app.services.ranking_service import RankingService
from app.schemas.score import RankingResponse, ExplainabilityReport

router = APIRouter()


@router.post("/jobs/{job_id}/rank", response_model=RankingResponse)
async def rank_candidates(
    job_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Trigger semantic ranking for all candidates of a job."""
    service = RankingService(db)
    return await service.rank_candidates_for_job(job_id)


@router.get("/jobs/{job_id}/rankings", response_model=RankingResponse)
async def get_rankings(
    job_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get existing ranking results for a job."""
    service = RankingService(db)
    return await service.get_rankings(job_id)


@router.get("/rankings/{score_id}/explain", response_model=ExplainabilityReport)
async def get_explanation(
    score_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Get explainability report for a specific candidate score."""
    service = RankingService(db)
    return await service.get_explanation(score_id)


@router.get("/jobs/{job_id}/rankings/export")
async def export_rankings_csv(
    job_id: int,
    recruiter_id: int = Depends(get_current_recruiter_id),
    db: AsyncSession = Depends(get_db),
):
    """Export rankings as CSV file."""
    service = RankingService(db)
    csv_content = await service.export_rankings_csv(job_id)
    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rankings_job_{job_id}.csv"},
    )

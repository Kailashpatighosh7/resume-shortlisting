"""
Score Schemas
=============
"""

from datetime import datetime
from typing import Optional, Any, List

from pydantic import BaseModel


class ScoreResponse(BaseModel):
    """Candidate score and explainability data."""
    id: int
    candidate_id: int
    job_id: int
    overall_score: float
    matched_skills: list = []
    missing_skills: list = []
    semantic_matches: list = []
    explanation: dict = {}
    scored_at: datetime

    model_config = {"from_attributes": True}


class RankingEntry(BaseModel):
    """Single entry in the ranking list."""
    rank: int
    candidate_id: int
    candidate_name: str
    candidate_email: str
    overall_score: float
    matched_skills: list = []
    missing_skills: list = []
    semantic_matches: list = []
    resume_filename: str = ""
    status: str = "new"


class RankingResponse(BaseModel):
    """Full ranking response for a job."""
    job_id: int
    job_title: str
    total_candidates: int
    shortlist_quota: int = 5
    rankings: List[RankingEntry]


class ExplainabilityReport(BaseModel):
    """Detailed explainability report for a single candidate-job pair."""
    candidate_id: int
    candidate_name: str
    job_id: int
    job_title: str
    overall_score: float
    matched_skills: list
    missing_skills: list
    semantic_matches: list
    skill_similarity_matrix: dict = {}
    explanation_text: str = ""

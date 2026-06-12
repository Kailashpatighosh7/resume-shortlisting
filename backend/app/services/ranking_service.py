"""
Ranking Service
===============
Orchestrates the semantic matching pipeline:
parse → embed → compare → score → rank → explain.
"""

import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.candidate_score import CandidateScore
from app.repositories.job_repo import JobRepository
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.resume_repo import ResumeRepository
from app.repositories.score_repo import ScoreRepository
from app.ai.matcher import compute_similarity, rank_candidates
from app.ai.explainer import generate_explanation
from app.schemas.score import (
    RankingEntry, RankingResponse, ScoreResponse, ExplainabilityReport,
)


class RankingService:
    """Orchestrates semantic matching and candidate ranking."""

    def __init__(self, db: AsyncSession):
        self.job_repo = JobRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.score_repo = ScoreRepository(db)
        self.db = db

    async def rank_candidates_for_job(self, job_id: int) -> RankingResponse:
        """
        Run the full ranking pipeline for a job.

        Steps:
        1. Load job and its JD embedding
        2. Load all candidates and their resume embeddings
        3. Compute cosine similarity scores
        4. Generate explainability reports
        5. Store scores in database
        6. Return ranked results
        """
        # 1. Load job
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")
        if not job.jd_embedding:
            raise NotFoundException("Job has no embedding. Please update the job description.")

        jd_embedding = json.loads(job.jd_embedding)

        # 2. Load candidates
        candidates, total = await self.candidate_repo.list_by_job(job_id, per_page=1000)
        if not candidates:
            return RankingResponse(
                job_id=job_id,
                job_title=job.title,
                total_candidates=0,
                shortlist_quota=job.shortlist_quota or 5,
                rankings=[],
            )

        # 3. Load resume embeddings
        candidate_ids = [c.id for c in candidates]
        resumes = await self.resume_repo.list_by_candidate_ids(candidate_ids)
        resume_map = {r.candidate_id: r for r in resumes}

        # Build candidate embeddings list
        candidate_embeddings = []
        for c in candidates:
            resume = resume_map.get(c.id)
            if resume and resume.resume_embedding:
                emb = json.loads(resume.resume_embedding)
                candidate_embeddings.append((c.id, emb))

        # 4. Rank by cosine similarity
        ranked = rank_candidates(jd_embedding, candidate_embeddings)

        # 5. Generate explainability and store scores
        candidate_map = {c.id: c for c in candidates}
        rankings = []

        ranked_ids = [cid for cid, _ in ranked]
        await self._apply_shortlist_quota(job, ranked_ids)

        for rank_idx, (cid, score) in enumerate(ranked, start=1):
            candidate = candidate_map[cid]
            resume = resume_map.get(cid)

            # Get parsed skills from resume
            resume_skills = []
            if resume and resume.parsed_data:
                resume_skills = resume.parsed_data.get("skills", [])

            # Generate explanation
            explanation_data = generate_explanation(
                resume_skills=resume_skills,
                required_skills_str=job.required_skills or "",
                preferred_skills_str=job.preferred_skills or "",
                overall_score=score,
            )

            # Store score in DB
            score_entry = CandidateScore(
                candidate_id=cid,
                job_id=job_id,
                overall_score=round(score, 4),
                matched_skills=explanation_data["matched_skills"],
                missing_skills=explanation_data["missing_skills"],
                semantic_matches=explanation_data["semantic_matches"],
                explanation=explanation_data["explanation"],
            )
            await self.score_repo.upsert(score_entry)

            rankings.append(RankingEntry(
                rank=rank_idx,
                candidate_id=cid,
                candidate_name=candidate.name,
                candidate_email=candidate.email or "",
                overall_score=round(score * 100, 1),
                matched_skills=explanation_data["matched_skills"],
                missing_skills=explanation_data["missing_skills"],
                semantic_matches=explanation_data["semantic_matches"],
                resume_filename=resume.original_filename if resume else "",
                status=candidate.status or "new",
            ))

        # Refresh candidate statuses after auto shortlist/reject
        candidates, _ = await self.candidate_repo.list_by_job(job_id, per_page=1000)
        candidate_map = {c.id: c for c in candidates}
        for entry in rankings:
            candidate = candidate_map.get(entry.candidate_id)
            if candidate:
                entry.status = candidate.status

        return RankingResponse(
            job_id=job_id,
            job_title=job.title,
            total_candidates=len(rankings),
            shortlist_quota=job.shortlist_quota or 5,
            rankings=rankings,
        )

    async def get_rankings(self, job_id: int) -> RankingResponse:
        """Get existing rankings for a job (without re-computing)."""
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job #{job_id} not found")

        scores = await self.score_repo.list_by_job(job_id)

        candidates, _ = await self.candidate_repo.list_by_job(job_id, per_page=1000)
        candidate_map = {c.id: c for c in candidates}

        candidate_ids = [c.id for c in candidates]
        resumes = await self.resume_repo.list_by_candidate_ids(candidate_ids)
        resume_map = {r.candidate_id: r for r in resumes}

        rankings = []
        for rank_idx, s in enumerate(scores, start=1):
            candidate = candidate_map.get(s.candidate_id)
            resume = resume_map.get(s.candidate_id)
            if candidate:
                rankings.append(RankingEntry(
                    rank=rank_idx,
                    candidate_id=s.candidate_id,
                    candidate_name=candidate.name,
                    candidate_email=candidate.email or "",
                    overall_score=round(s.overall_score * 100, 1),
                    matched_skills=s.matched_skills or [],
                    missing_skills=s.missing_skills or [],
                    semantic_matches=s.semantic_matches or [],
                    resume_filename=resume.original_filename if resume else "",
                    status=candidate.status or "new",
                ))

        return RankingResponse(
            job_id=job_id,
            job_title=job.title,
            total_candidates=len(rankings),
            shortlist_quota=job.shortlist_quota or 5,
            rankings=rankings,
        )

    async def _apply_shortlist_quota(self, job, ranked_candidate_ids: List[int]) -> None:
        """Auto-shortlist top N candidates and reject the rest."""
        quota = job.shortlist_quota or 5
        shortlist_ids = set(ranked_candidate_ids[:quota])

        for cid in ranked_candidate_ids:
            candidate = await self.candidate_repo.get_by_id(cid)
            if not candidate:
                continue
            candidate.status = "shortlisted" if cid in shortlist_ids else "rejected"
            await self.candidate_repo.update(candidate)

    async def get_explanation(self, score_id: int) -> ExplainabilityReport:
        """Get detailed explainability report for a score entry."""
        score = await self.score_repo.get_by_id(score_id)
        if not score:
            raise NotFoundException(f"Score #{score_id} not found")

        candidate = await self.candidate_repo.get_by_id(score.candidate_id)
        job = await self.job_repo.get_by_id(score.job_id)

        return ExplainabilityReport(
            candidate_id=score.candidate_id,
            candidate_name=candidate.name if candidate else "",
            job_id=score.job_id,
            job_title=job.title if job else "",
            overall_score=round(score.overall_score * 100, 1),
            matched_skills=score.matched_skills or [],
            missing_skills=score.missing_skills or [],
            semantic_matches=score.semantic_matches or [],
            explanation_text=score.explanation.get("text", "") if score.explanation else "",
        )

    async def export_rankings_csv(self, job_id: int) -> str:
        """Generate CSV content for rankings export."""
        ranking = await self.get_rankings(job_id)
        lines = ["Rank,Candidate,Email,Score(%),Matched Skills,Missing Skills,Resume"]
        for r in ranking.rankings:
            matched = "; ".join(r.matched_skills)
            missing = "; ".join(r.missing_skills)
            lines.append(
                f'{r.rank},"{r.candidate_name}","{r.candidate_email}",'
                f'{r.overall_score},"{matched}","{missing}","{r.resume_filename}"'
            )
        return "\n".join(lines)

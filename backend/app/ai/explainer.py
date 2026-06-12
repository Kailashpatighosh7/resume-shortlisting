"""
Explainable AI Module
=====================
Provides hybrid explainability for candidate-job matches:
1. Exact skill matching (keyword-level)
2. Semantic skill similarity (embedding-level)
3. Natural language explanation generation
"""

from typing import List, Dict, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def generate_explanation(
    resume_skills: List[str],
    required_skills_str: str,
    preferred_skills_str: str,
    overall_score: float,
) -> Dict:
    """
    Generate a hybrid explainability report.

    Combines exact keyword matching with semantic similarity analysis
    to explain why a candidate scored the way they did.

    Args:
        resume_skills: Skills extracted from the resume.
        required_skills_str: Comma-separated required skills from JD.
        preferred_skills_str: Comma-separated preferred skills from JD.
        overall_score: The overall semantic similarity score.

    Returns:
        Dictionary with matched_skills, missing_skills, semantic_matches, and explanation.
    """
    # Parse required and preferred skills
    required_skills = _parse_skills(required_skills_str)
    preferred_skills = _parse_skills(preferred_skills_str)
    all_jd_skills = required_skills + preferred_skills

    # Normalize for comparison
    resume_skills_lower = {s.lower().strip() for s in resume_skills}
    jd_skills_lower = {s.lower().strip() for s in all_jd_skills}

    # Exact matches
    matched = resume_skills_lower & jd_skills_lower
    missing = jd_skills_lower - resume_skills_lower

    # Semantic matches: find near-matches between unmatched resume skills and missing JD skills
    semantic_matches = _find_semantic_matches(
        list(resume_skills_lower - matched),
        list(missing),
    )

    # Update missing based on semantic matches
    semantically_matched_jd = {m["jd_skill"] for m in semantic_matches}
    truly_missing = missing - semantically_matched_jd

    # Generate text explanation
    explanation_text = _generate_text_explanation(
        overall_score, matched, truly_missing, semantic_matches
    )

    return {
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(truly_missing)),
        "semantic_matches": semantic_matches,
        "explanation": {
            "overall_score_pct": round(overall_score * 100, 1),
            "exact_match_count": len(matched),
            "semantic_match_count": len(semantic_matches),
            "missing_count": len(truly_missing),
            "total_required": len(required_skills),
            "total_preferred": len(preferred_skills),
            "text": explanation_text,
        },
    }


def _parse_skills(skills_str: str) -> List[str]:
    """Parse comma-separated skills string."""
    if not skills_str:
        return []
    return [s.strip() for s in skills_str.split(",") if s.strip()]


def _find_semantic_matches(
    resume_skills: List[str],
    missing_jd_skills: List[str],
    threshold: float = 0.55,
) -> List[Dict]:
    """
    Find semantically similar skill pairs between resume and JD.

    Uses the embedding model to compute pairwise similarity.
    """
    if not resume_skills or not missing_jd_skills:
        return []

    try:
        from app.ai.embedding import get_embeddings_batch

        resume_embs = get_embeddings_batch(resume_skills)
        jd_embs = get_embeddings_batch(missing_jd_skills)

        sim_matrix = cosine_similarity(
            np.array(resume_embs), np.array(jd_embs)
        )

        matches = []
        for i, resume_skill in enumerate(resume_skills):
            for j, jd_skill in enumerate(missing_jd_skills):
                score = float(sim_matrix[i][j])
                if score >= threshold:
                    matches.append({
                        "resume_skill": resume_skill,
                        "jd_skill": jd_skill,
                        "similarity": round(score, 3),
                    })

        # Sort by similarity descending and deduplicate JD skills
        matches.sort(key=lambda m: m["similarity"], reverse=True)
        seen_jd = set()
        unique_matches = []
        for m in matches:
            if m["jd_skill"] not in seen_jd:
                unique_matches.append(m)
                seen_jd.add(m["jd_skill"])

        return unique_matches[:10]  # Limit results

    except Exception:
        return []


def _generate_text_explanation(
    score: float,
    matched: set,
    missing: set,
    semantic_matches: List[Dict],
) -> str:
    """Generate a human-readable explanation text."""
    pct = round(score * 100, 1)
    lines = [f"Overall Match Score: {pct}%\n"]

    if matched:
        lines.append(f"✅ Exact Skill Matches ({len(matched)}):")
        for s in sorted(matched):
            lines.append(f"   • {s.title()}")
        lines.append("")

    if semantic_matches:
        lines.append(f"🔄 Semantic Matches ({len(semantic_matches)}):")
        for m in semantic_matches:
            lines.append(
                f"   • {m['resume_skill'].title()} → "
                f"{m['jd_skill'].title()} ({round(m['similarity']*100)}%)"
            )
        lines.append("")

    if missing:
        lines.append(f"❌ Missing Skills ({len(missing)}):")
        for s in sorted(missing):
            lines.append(f"   • {s.title()}")
        lines.append("")

    # Overall assessment
    if pct >= 80:
        lines.append("🌟 Strong Match — Candidate is highly qualified for this role.")
    elif pct >= 60:
        lines.append("👍 Good Match — Candidate meets most requirements.")
    elif pct >= 40:
        lines.append("⚠️ Moderate Match — Candidate has relevant but incomplete skill coverage.")
    else:
        lines.append("❌ Weak Match — Significant skill gaps identified.")

    return "\n".join(lines)

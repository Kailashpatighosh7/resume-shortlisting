"""
Semantic Matcher
================
Computes cosine similarity between resume and job description embeddings.
Uses scikit-learn for accurate cosine similarity computation.
"""

from typing import List, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(embedding_a: List[float], embedding_b: List[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Args:
        embedding_a: First embedding vector (e.g., resume).
        embedding_b: Second embedding vector (e.g., job description).

    Returns:
        Cosine similarity score between 0.0 and 1.0.
    """
    vec_a = np.array(embedding_a).reshape(1, -1)
    vec_b = np.array(embedding_b).reshape(1, -1)
    similarity = cosine_similarity(vec_a, vec_b)[0][0]
    # Clamp to [0, 1] range
    return float(max(0.0, min(1.0, similarity)))


def rank_candidates(
    job_embedding: List[float],
    candidate_embeddings: List[Tuple[int, List[float]]],
) -> List[Tuple[int, float]]:
    """
    Rank candidates by similarity to a job description.

    Args:
        job_embedding: The job description embedding vector.
        candidate_embeddings: List of (candidate_id, embedding_vector) tuples.

    Returns:
        Sorted list of (candidate_id, score) tuples, highest score first.
    """
    if not candidate_embeddings:
        return []

    job_vec = np.array(job_embedding).reshape(1, -1)
    candidate_ids = [c[0] for c in candidate_embeddings]
    candidate_vecs = np.array([c[1] for c in candidate_embeddings])

    similarities = cosine_similarity(job_vec, candidate_vecs)[0]

    ranked = list(zip(candidate_ids, [float(s) for s in similarities]))
    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked

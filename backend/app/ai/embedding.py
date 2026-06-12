"""
Embedding Service
=================
Generates text embeddings using Sentence Transformers (all-MiniLM-L6-v2).

Uses a singleton pattern so the model is loaded only once.
"""

from typing import List

from app.core.config import settings

# ── Singleton Model Instance ─────────────────────────────────

_model = None


def _get_model():
    """Lazy-load the SentenceTransformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"📦 Loading AI model: {settings.AI_MODEL_NAME}...")
        _model = SentenceTransformer(settings.AI_MODEL_NAME)
        print("✅ AI model loaded successfully")
    return _model


# ── Public API ────────────────────────────────────────────────

def get_embedding(text: str) -> List[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.

    Args:
        text: Input text (resume content, job description, etc.)

    Returns:
        A list of floats representing the text embedding.
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts at once (more efficient).

    Args:
        texts: List of input strings.

    Returns:
        List of embedding vectors.
    """
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, batch_size=32)
    return [e.tolist() for e in embeddings]

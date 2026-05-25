from dataclasses import dataclass
from functools import lru_cache

import numpy as np

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.5


@dataclass
class HallucinationResult:
    flagged: bool
    similarity: float
    explanation: str


@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def detect(response: str, source_docs: list[str]) -> HallucinationResult:
    if not source_docs:
        return HallucinationResult(flagged=False, similarity=1.0, explanation="no source docs provided")

    model = _load_model()
    resp_emb = model.encode(response, normalize_embeddings=True)
    src_embs = model.encode(source_docs, normalize_embeddings=True)

    similarities = [_cosine(resp_emb, s) for s in src_embs]
    max_sim = max(similarities)

    flagged = max_sim < SIMILARITY_THRESHOLD
    explanation = (
        f"response similarity to best source: {max_sim:.3f} "
        f"({'below' if flagged else 'above'} threshold {SIMILARITY_THRESHOLD})"
    )

    return HallucinationResult(flagged=flagged, similarity=max_sim, explanation=explanation)

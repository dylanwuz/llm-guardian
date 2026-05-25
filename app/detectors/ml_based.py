from dataclasses import dataclass
from functools import lru_cache

MODEL_NAME = "deepset/deberta-v3-base-injection"


@dataclass
class MLResult:
    flagged: bool
    confidence: float  # 0.0 ~ 1.0
    label: str


@lru_cache(maxsize=1)
def _load_pipeline():
    from transformers import pipeline
    return pipeline("text-classification", model=MODEL_NAME)


def detect(prompt: str, threshold: float = 0.5) -> MLResult:
    pipe = _load_pipeline()
    result = pipe(prompt, truncation=True, max_length=512)[0]
    score: float = result["score"]

    # 模型輸出 label: "INJECTION" or "LEGITIMATE"
    is_injection = result["label"].upper() == "INJECTION"
    flagged = is_injection and score >= threshold

    return MLResult(
        flagged=flagged,
        confidence=score if is_injection else 1 - score,
        label=result["label"],
    )

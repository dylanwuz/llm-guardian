import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    r"ignore (previous|all|above|prior) instructions?",
    r"disregard (previous|all|above|prior) instructions?",
    r"forget (everything|all|what) (you|i).{0,20}(told|said|instructed)",
    r"you are now",
    r"act as (a|an|if)",
    r"new (role|persona|identity|instructions?)",
    r"system (prompt|instructions?)",
    r"reveal (your|the) (instructions?|prompt|system)",
    r"what (are|were) your instructions?",
    r"print (your|the|them) (instructions?|prompt)?",
    r"print.*verbatim",
    r"jailbreak",
    r"DAN (mode|prompt)",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


@dataclass
class RuleResult:
    flagged: bool
    matched_patterns: list[str]
    risk_score: float  # 0.0 ~ 1.0


def detect(prompt: str) -> RuleResult:
    matched = [p.pattern for p in _compiled if p.search(prompt)]
    risk_score = min(len(matched) * 0.3, 1.0)
    return RuleResult(
        flagged=len(matched) > 0,
        matched_patterns=matched,
        risk_score=risk_score,
    )

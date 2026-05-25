from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.detectors import rule_based, ml_based, hallucination
from app.llm_client import chat

app = FastAPI(title="LLM Guardian", version="0.1.0")


class PromptRequest(BaseModel):
    prompt: str
    source_docs: list[str] = []
    use_ml: bool = True
    check_hallucination: bool = False


class GuardResponse(BaseModel):
    blocked: bool
    risk_score: float
    rule_result: dict
    ml_result: dict | None
    hallucination_result: dict | None
    llm_response: str | None


@app.post("/guard", response_model=GuardResponse)
def guard(req: PromptRequest):
    rule_res = rule_based.detect(req.prompt)

    ml_res = None
    if req.use_ml:
        ml_res = ml_based.detect(req.prompt)

    # 任一層偵測到 injection 即阻擋
    injection_flagged = rule_res.flagged or (ml_res is not None and ml_res.flagged)

    if injection_flagged:
        return GuardResponse(
            blocked=True,
            risk_score=max(rule_res.risk_score, ml_res.confidence if ml_res else 0.0),
            rule_result={"flagged": rule_res.flagged, "matched_patterns": rule_res.matched_patterns, "risk_score": rule_res.risk_score},
            ml_result={"flagged": ml_res.flagged, "confidence": ml_res.confidence, "label": ml_res.label} if ml_res else None,
            hallucination_result=None,
            llm_response=None,
        )

    llm_response = chat(req.prompt)

    hall_res = None
    if req.check_hallucination and req.source_docs:
        hall_res = hallucination.detect(llm_response, req.source_docs)

    return GuardResponse(
        blocked=False,
        risk_score=rule_res.risk_score,
        rule_result={"flagged": rule_res.flagged, "matched_patterns": rule_res.matched_patterns, "risk_score": rule_res.risk_score},
        ml_result={"flagged": ml_res.flagged, "confidence": ml_res.confidence, "label": ml_res.label} if ml_res else None,
        hallucination_result={"flagged": hall_res.flagged, "similarity": hall_res.similarity, "explanation": hall_res.explanation} if hall_res else None,
        llm_response=llm_response,
    )


@app.get("/health")
def health():
    return {"status": "ok"}

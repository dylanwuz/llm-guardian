import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.detectors.rule_based import detect

with open(Path(__file__).parent / "test_cases.json") as f:
    _cases = json.load(f)

_injection = [(c["id"], c["prompt"]) for c in _cases["injection_attacks"]]
_legitimate = [(c["id"], c["prompt"]) for c in _cases["legitimate_prompts"]]


@pytest.mark.parametrize("case_id,prompt", _injection)
def test_injection_blocked(case_id, prompt):
    result = detect(prompt)
    assert result.flagged, f"{case_id}: expected flagged but got passed (prompt: {prompt[:60]})"


@pytest.mark.parametrize("case_id,prompt", _legitimate)
def test_legitimate_passed(case_id, prompt):
    result = detect(prompt)
    assert not result.flagged, f"{case_id}: expected passed but got flagged (prompt: {prompt[:60]})"
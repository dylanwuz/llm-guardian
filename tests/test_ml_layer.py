import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.detectors.ml_based import detect

with open(Path(__file__).parent / "test_cases.json") as f:
    cases = json.load(f)

print("載入模型中（首次執行會下載約 500MB）...\n")

results = {"injection": {"pass": 0, "total": 0}, "legitimate": {"pass": 0, "total": 0}}

for prompt_data in cases["injection_attacks"]:
    result = detect(prompt_data["prompt"])
    expected_blocked = True
    ok = result.flagged == expected_blocked
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {prompt_data['id']} | flagged={result.flagged} conf={result.confidence:.2f} | {prompt_data['prompt'][:50]}")
    results["injection"]["total"] += 1
    if ok:
        results["injection"]["pass"] += 1

print()

for prompt_data in cases["legitimate_prompts"]:
    result = detect(prompt_data["prompt"])
    expected_blocked = False
    ok = result.flagged == expected_blocked
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {prompt_data['id']} | flagged={result.flagged} conf={result.confidence:.2f} | {prompt_data['prompt'][:50]}")
    results["legitimate"]["total"] += 1
    if ok:
        results["legitimate"]["pass"] += 1

inj = results["injection"]
leg = results["legitimate"]
total_pass = inj["pass"] + leg["pass"]
total = inj["total"] + leg["total"]

print(f"""
Injection accuracy:  {inj['pass']}/{inj['total']} ({inj['pass']/inj['total']*100:.0f}%)
Legitimate accuracy: {leg['pass']}/{leg['total']} ({leg['pass']/leg['total']*100:.0f}%)
Overall accuracy:    {total_pass}/{total} ({total_pass/total*100:.0f}%)
""")

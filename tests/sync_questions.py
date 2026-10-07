import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
gt = json.loads((ROOT / "data" / "ground_truth.json").read_text(encoding="utf-8"))
qs = [
    {"id": g["id"], "question": g["question"],
     "expected_status": "ok" if g["answerable"] else "cannot_determine"}
    for g in gt
]
(ROOT / "tests" / "questions.json").write_text(
    json.dumps(qs, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(qs)} questions")
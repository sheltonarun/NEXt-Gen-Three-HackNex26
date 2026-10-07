import json
import math
from pathlib import Path
from agent.agent import run_agent
from verifier.verify import verify

ROOT = Path(__file__).resolve().parent.parent
TRUTH = ROOT / "data" / "ground_truth.json"
SCRIPTS_DIR = ROOT / "outputs" / "scripts"
REPORT = ROOT / "outputs" / "results" / "eval_report.json"

def grade(r, gt):
    if gt["answerable"]:
        if r.status != "answered":
            return False
        try:
            expected = float(gt["answer"])
            got = float(r.answer)
            return math.isclose(expected, got, rel_tol=1e-4, abs_tol=1e-4)
        except (ValueError, TypeError):
            return False
    else:
        return r.status == "refused"

def main():
    if not TRUTH.exists():
        print(f"Ground truth not found at {TRUTH}")
        return
        
    truth = json.loads(TRUTH.read_text(encoding="utf-8"))
    rows = []

    for gt in truth:
        qid = gt["id"].lower()
        if gt["answerable"] and str(gt.get("answer")).strip().upper() == "TBD":
            print(f"SKIP {qid}: ground truth is TBD")
            continue
        try:
            r = run_agent(gt["question"], name=qid)
        except Exception as e:
            rows.append({"id": qid, "correct": False, "verified": None, "error": str(e)})
            print(f"ERROR {qid}: {e}")
            continue

        correct = grade(r, gt)
        verified = None
        if r.status == "answered":
            script_path = SCRIPTS_DIR / f"{qid}.py"
            verify_res = verify(script_path, r.answer)
            verified = verify_res.get("passed", False) if isinstance(verify_res, dict) else False

        expected = gt.get("answer") if gt["answerable"] else "REFUSE"
        rows.append({
            "id": qid, 
            "expected": expected,
            "status": r.status, 
            "answer": r.answer,
            "refusal_reason": getattr(r, 'refusal_reason', None),
            "assumptions": getattr(r, 'assumptions', None),
            "correct": correct, 
            "verified": verified,
        })
        print(f"{'PASS' if correct else 'FAIL'} {qid} | {r.status} | got={r.answer} | expected={expected} | verified={verified}")

    total = len(rows)
    n_correct = sum(bool(r.get("correct")) for r in rows)
    answered = [r for r in rows if r.get("verified") is not None]
    n_verified = sum(1 for r in answered if r.get("verified"))

    print("\n=== SUMMARY ===")
    print(f"Correct:  {n_correct}/{total}")
    print(f"Verified: {n_verified}/{len(answered)} answered questions re-ran to the same number")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report saved to {REPORT}")

if __name__ == "__main__":
    main()
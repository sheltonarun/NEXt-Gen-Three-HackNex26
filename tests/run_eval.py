import json
import math
import sys
from concurrent.futures import ThreadPoolExecutor
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
            expected = float(str(gt["answer"]).replace(",", ""))
            got = float(str(r.answer).replace(",", ""))
            return math.isclose(expected, got, rel_tol=1e-4, abs_tol=1e-4)
        except (ValueError, TypeError):
            return False
    return r.status == "refused"


def evaluate(gt):
    qid = gt["id"].lower()
    try:
        r = run_agent(gt["question"], name=qid)
    except Exception as e:
        print(f"ERROR {qid}: {e}", flush=True)
        return {"id": qid, "correct": False, "verified": None, "error": str(e)}

    correct = grade(r, gt)
    verified = None
    if r.status == "answered":
        res = verify(SCRIPTS_DIR / f"{qid}.py", r.answer)
        verified = res.get("passed", False) if isinstance(res, dict) else False

    expected = gt.get("answer") if gt["answerable"] else "REFUSE"
    print(f"{'PASS' if correct else 'FAIL'} {qid} | {r.status} | got={r.answer} | "
          f"expected={expected} | verified={verified}", flush=True)
    return {
        "id": qid, "expected": expected, "status": r.status, "answer": r.answer,
        "refusal_reason": getattr(r, "refusal_reason", None),
        "assumptions": getattr(r, "assumptions", None),
        "correct": correct, "verified": verified,
    }


def main():
    if not TRUTH.exists():
        print(f"Ground truth not found at {TRUTH}")
        return

    truth = json.loads(TRUTH.read_text(encoding="utf-8"))
    only = [a.lower() for a in sys.argv[1:]]        # e.g. python -m tests.run_eval q03 q07

    todo = []
    for gt in truth:
        qid = gt["id"].lower()
        if gt["answerable"] and str(gt.get("answer")).strip().upper() == "TBD":
            print(f"SKIP {qid}: ground truth is TBD")
            continue
        if only and qid not in only:
            continue
        todo.append(gt)

    with ThreadPoolExecutor(max_workers=3) as ex:
        rows = list(ex.map(evaluate, todo))

    total = len(rows)
    n_correct = sum(bool(r.get("correct")) for r in rows)
    answered = [r for r in rows if r.get("verified") is not None]
    n_verified = sum(1 for r in answered if r.get("verified"))

    print("\n=== SUMMARY ===")
    print(f"Correct:  {n_correct}/{total}")
    print(f"Verified: {n_verified}/{len(answered)} answered questions re-ran to the same number")
    print("Failed:   " + (", ".join(r["id"] for r in rows if not r.get("correct")) or "none"))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report saved to {REPORT}")


if __name__ == "__main__":
    main()
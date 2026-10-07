from agent.executor import run_script, parse_number
from verifier.compare import numbers_match


def verify(script_path, claimed_answer, ground_truth=None) -> dict:
    ok, out = run_script(script_path)
    if not ok:
        return {"passed": False, "reason": f"script failed: {out}"}
    try:
        rerun = parse_number(out)
    except Exception:
        return {"passed": False, "reason": f"output not a number: {out}"}

    passed = numbers_match(rerun, float(claimed_answer))
    result = {"passed": passed, "rerun_value": rerun, "claimed": claimed_answer}
    if ground_truth is not None:
        result["matches_ground_truth"] = numbers_match(rerun, float(ground_truth))
    return result
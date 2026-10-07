import re
from agent.schema import AgentResult
from agent.llm_client import ask_llm
from agent.prompts import SYSTEM_PROMPT, build_user_prompt
from agent.data_profiler import profile_data
from agent.executor import save_script, run_script, parse_number
from agent.refusal import parse_refusal


def extract_code(text: str):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None


def extract_assumptions(code: str):
    return [
        line.split("ASSUMPTION:", 1)[1].strip()
        for line in code.splitlines() if "ASSUMPTION:" in line
    ]


def run_agent(question: str, name: str = "q", max_retries: int = 2) -> AgentResult:
    profile = profile_data()
    error, prev_code = None, None

    for _ in range(max_retries + 1):
        reply = ask_llm(SYSTEM_PROMPT, build_user_prompt(question, profile, error, prev_code))

        reason = parse_refusal(reply)
        if reason:
            return AgentResult(question, "refused", refusal_reason=reason)

        code = extract_code(reply)
        if not code:
            error = "No python code block found. Reply with one ```python block or REFUSE: reason."
            continue

        prev_code = code
        path = save_script(code, name)
        ok, out = run_script(path)
        if not ok:
            error = out
            continue
        try:
            answer = parse_number(out)
        except Exception:
            error = f"Last line of output was not a number: {out[-200:]}"
            continue

        return AgentResult(question, "answered", answer, extract_assumptions(code), code)

    return AgentResult(
        question, "refused",
        refusal_reason=f"Could not produce a working script. Last error: {error}",
    )
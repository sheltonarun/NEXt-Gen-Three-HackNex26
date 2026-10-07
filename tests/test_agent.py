import json
from agent.agent import run_agent
from agent.executor import SCRIPTS_DIR
from verifier.verify import verify

QUESTIONS = [
    "What is the total USD revenue in Q3 2025?",   # expect 350
    "What was the total revenue in Q3 2025?",      # expect refusal (EUR, no rate)
]

for i, q in enumerate(QUESTIONS, 1):
    r = run_agent(q, name=f"q{i}")
    print(json.dumps(r.to_dict(), indent=2, ensure_ascii=False))
    if r.status == "answered":
        print("VERIFY:", verify(SCRIPTS_DIR / f"q{i}.py", r.answer))
    print("-" * 40)
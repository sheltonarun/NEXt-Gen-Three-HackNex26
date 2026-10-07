# HackNex26 - PS08 Proof-Carrying Data Analyst

## What this project is
An LLM agent that answers questions about messy CSVs and text documents. Every numeric
answer ships with a standalone Python script that a verifier re-runs. If the script fails
or gives a different number, the answer is wrong. Unanswerable or trap questions must be
REFUSED with a reason (mixed currencies with no exchange rate, ambiguous dates, missing
data, conflicting values, forecasts, data that does not exist).

## My role (Person 3): agent/ and verifier/ ONLY
- agent/: schema.py, llm_client.py (Gemini, google-genai, retry + fallback), data_profiler.py,
  prompts.py, refusal.py, executor.py, agent.py
- verifier/: verify.py, compare.py
- tests/: run_eval.py, sync_questions.py, test_agent.py
- Other people own backend/ and frontend/ and data/. Do NOT edit those folders.

## Contract
agent/schema.py AgentResult: question, status ("answered"|"refused"), answer, assumptions,
code, refusal_reason. Do not change it without asking me.
Public functions: run_agent(question, name) -> AgentResult ; verify(script_path, claimed_answer) -> dict

## How it works
profile_data() reads data/raw/*.csv and data/docs/*.txt|md -> prompt -> LLM replies with
either one ```python block (with "# ASSUMPTION:" comments, last line prints one number) or
"REFUSE: reason" -> script saved to outputs/scripts and run in a subprocess -> retry on error.
Grading data: data/ground_truth.json (list of objects: id, question, answerable, answer,
refusal_reason).

## Rules
- NEVER write API keys anywhere. Keys live only in .env (git-ignored). Read via os.getenv.
- Keep code simple and readable. No new dependencies without telling me.
- Fix failures with GENERAL rules in prompts.py / data_profiler.py, never rules that only fit
  one test question (the judges use a different dataset).
- Never invent data, exchange rates or ground-truth answers.
- Do not run git commit or git push. I do that myself.
- After each change, tell me what changed and which command to run to test it.
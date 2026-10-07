from pathlib import Path

ROOT = Path(".")  # run this inside HackNex26

dirs = [
    "data/raw", "data/docs",
    "agent", "verifier",
    "outputs/scripts", "outputs/results",
    "tests", "backend", "frontend",
]

files = {
    "README.md": "# HackNex26 - PS08 Proof-Carrying Data Analyst\n",
    "requirements.txt": "pandas\nnumpy\npython-dotenv\nfastapi\nuvicorn\n",
    ".env.example": "LLM_API_KEY=your_key_here\n",
    ".gitignore": ".env\n__pycache__/\n*.pyc\n.venv/\noutputs/\n",
    "AGENTS.md": (
        "# Project rules\n"
        "- Every numeric answer must ship with a standalone Python script "
        "that loads the CSVs itself and prints one number.\n"
        "- Never invent data or exchange rates; refuse with a reason instead.\n"
        "- Keep code simple and readable.\n"
        "- The JSON contract in agent/schema.py is the single source of truth: "
        "question, status (answered|refused), answer, assumptions, code, refusal_reason.\n"
    ),
    "data/ground_truth.json": "{}\n",
    "agent/__init__.py": "",
    "agent/agent.py": "",
    "agent/prompts.py": "",
    "agent/llm_client.py": "",
    "agent/data_profiler.py": "",
    "agent/executor.py": "",
    "agent/refusal.py": "",
    "agent/schema.py": "",
    "verifier/__init__.py": "",
    "verifier/verify.py": "",
    "verifier/compare.py": "",
    "tests/questions.json": "[]\n",
    "tests/test_agent.py": "",
    "tests/test_verifier.py": "",
    "tests/run_eval.py": "",
    "backend/.gitkeep": "",
    "frontend/.gitkeep": "",
    "data/raw/.gitkeep": "",
    "data/docs/.gitkeep": "",
    "outputs/scripts/.gitkeep": "",
    "outputs/results/.gitkeep": "",
}

for d in dirs:
    (ROOT / d).mkdir(parents=True, exist_ok=True)

for path, content in files.items():
    p = ROOT / path
    if not p.exists():  # never overwrite existing work
        p.write_text(content, encoding="utf-8")

print("Structure created.")
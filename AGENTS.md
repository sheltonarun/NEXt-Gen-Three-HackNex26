# Project rules
- Every numeric answer must ship with a standalone Python script that loads the CSVs itself and prints one number.
- Never invent data or exchange rates; refuse with a reason instead.
- Keep code simple and readable.
- The JSON contract in agent/schema.py is the single source of truth: question, status (answered|refused), answer, assumptions, code, refusal_reason.

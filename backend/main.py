import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import AnalyzeRequest, AnalyzeResponse, RunRecord
from backend.run_history import save_run, get_all_runs, get_run

# ── Agent (Person 3) ──────────────────────────────────────────────────────────
from agent.agent import run_agent
from agent.executor import save_script
from verifier.verify import verify


# ── Startup: ensure run_history table exists in Supabase ─────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once at server startup before accepting requests."""
    try:
        from backend.db import ensure_table
        ensure_table()
        print("[startup] run_history table ready.")
    except Exception as e:
        print(f"[startup] WARNING: Could not auto-create table: {e}")
        print("[startup] Create it manually in Supabase SQL editor — see README.")
    yield  # server runs here
    # (shutdown logic goes here if needed)


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Proof-Carrying Data Analyst API",
    description="Backend for HackNex26 PS08 — connects frontend, agent, and run history DB.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow Streamlit frontend (any origin during hackathon)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Quick liveness check — frontend uses this to detect if backend is up."""
    return {"status": "ok", "service": "proof-carrying-data-analyst"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Main endpoint.
    1. Calls the agent with the question.
    2. If answered: saves the script and verifies it.
    3. Saves the full result to Supabase run_history.
    4. Returns the AnalyzeResponse to the frontend.
    """
    question = request.question.strip()
    run_name = f"run_{uuid.uuid4().hex[:8]}"

    # ── Step 1: Run the agent ─────────────────────────────────────────────────
    agent_result = run_agent(question, name=run_name)

    # ── Step 2: Verify the proof script (only if answered + code exists) ──────
    verified = False
    if agent_result.status == "answered" and agent_result.code:
        from agent.executor import SCRIPTS_DIR
        script_path = SCRIPTS_DIR / f"{run_name}.py"
        if script_path.exists():
            try:
                v = verify(script_path, str(agent_result.answer))
                verified = v.get("passed", False)
            except Exception as e:
                print(f"[verify] Warning: {e}")

    # ── Step 3: Build response ────────────────────────────────────────────────
    response = AnalyzeResponse(
        question=agent_result.question,
        status=agent_result.status,
        answer=str(agent_result.answer) if agent_result.answer is not None else None,
        assumptions=agent_result.assumptions or [],
        code=agent_result.code or "",
        refusal_reason=agent_result.refusal_reason,
        verified=verified,
    )

    # ── Step 4: Persist to Supabase ───────────────────────────────────────────
    try:
        save_run(response)
    except Exception as e:
        print(f"[db] Warning: Could not save run to Supabase: {e}")

    return response


@app.get("/runs", response_model=list[RunRecord])
def list_runs() -> list[RunRecord]:
    """Return all past runs from Supabase, newest first."""
    try:
        return get_all_runs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch run history: {e}")


@app.get("/runs/{run_id}", response_model=RunRecord)
def get_single_run(run_id: str) -> RunRecord:
    """Return one specific run by its UUID."""
    try:
        record = get_run(run_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    if record is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return record

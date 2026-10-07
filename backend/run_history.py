from datetime import datetime, timezone
from typing import Optional
from backend.db import get_client
from backend.models import AnalyzeResponse, RunRecord


def save_run(result: AnalyzeResponse) -> Optional[str]:
    """
    Insert one agent result into the run_history table in Supabase.
    Returns the generated UUID of the new row, or None on failure.
    """
    client = get_client()
    row = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question":       result.question,
        "status":         result.status,
        "answer":         result.answer,
        "assumptions":    result.assumptions,   # stored as JSONB
        "code":           result.code,
        "refusal_reason": result.refusal_reason,
        "verified":       result.verified,
    }
    response = (
        client.table("run_history")
        .insert(row)
        .execute()
    )
    if response.data:
        return response.data[0].get("id")
    return None


def get_all_runs() -> list[RunRecord]:
    """
    Fetch all rows from run_history ordered by newest first.
    Returns a list of RunRecord objects.
    """
    client = get_client()
    response = (
        client.table("run_history")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return [RunRecord(**dict(row)) for row in (response.data or [])]


def get_run(run_id: str) -> Optional[RunRecord]:
    """
    Fetch a single run by its UUID.
    Returns a RunRecord or None if not found.
    """
    client = get_client()
    response = (
        client.table("run_history")
        .select("*")
        .eq("id", run_id)
        .limit(1)
        .execute()
    )
    if response.data:
        return RunRecord(**dict(response.data[0]))
    return None

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    """Return a singleton Supabase client."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env"
            )
        _client = create_client(url, key)
    return _client


def ensure_table() -> None:
    """
    Create the run_history table in Supabase if it does not already exist.
    Called once at server startup from main.py.
    Uses the Supabase REST API via rpc (raw SQL).
    """
    client = get_client()
    sql = """
    CREATE TABLE IF NOT EXISTS run_history (
        id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        question    TEXT NOT NULL,
        status      TEXT NOT NULL,
        answer      TEXT,
        assumptions JSONB,
        code        TEXT,
        refusal_reason TEXT,
        verified    BOOLEAN NOT NULL DEFAULT FALSE
    );
    """
    client.rpc("exec_sql", {"query": sql}).execute()

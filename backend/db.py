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
    Verify the run_history table exists by doing a lightweight SELECT.
    The table must be created once manually in Supabase SQL editor.

    SQL to run in Supabase → SQL Editor:
        CREATE TABLE IF NOT EXISTS run_history (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            question        TEXT NOT NULL,
            status          TEXT NOT NULL,
            answer          TEXT,
            assumptions     JSONB,
            code            TEXT,
            refusal_reason  TEXT,
            verified        BOOLEAN NOT NULL DEFAULT FALSE
        );
        ALTER TABLE run_history DISABLE ROW LEVEL SECURITY;
    """
    client = get_client()
    # Simple ping — raises if table doesn't exist
    client.table("run_history").select("id").limit(1).execute()

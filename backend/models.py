from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnalyzeRequest(BaseModel):
    """What the frontend sends to POST /analyze."""
    question: str = Field(..., min_length=5, description="The question to ask about the dataset")


class AnalyzeResponse(BaseModel):
    """What the backend returns from POST /analyze — matches AgentResult + verified flag."""
    question: str
    status: str                          # "answered" | "refused"
    answer: Optional[str] = None
    assumptions: List[str] = []
    code: str = ""
    refusal_reason: Optional[str] = None
    verified: bool = False


class RunRecord(BaseModel):
    """A single row from the run_history table in Supabase."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    question: str
    status: str
    answer: Optional[str] = None
    assumptions: List[str] = []
    code: str = ""
    refusal_reason: Optional[str] = None
    verified: bool = False

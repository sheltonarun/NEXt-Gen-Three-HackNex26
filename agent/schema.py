from dataclasses import dataclass, field, asdict
from typing import Optional, Any


@dataclass
class AgentResult:
    question: str
    status: str                      # "answered" | "refused"
    answer: Optional[Any] = None
    assumptions: list = field(default_factory=list)
    code: str = ""
    refusal_reason: Optional[str] = None

    def to_dict(self):
        return asdict(self)
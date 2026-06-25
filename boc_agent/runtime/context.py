import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from boc_agent.skill.models import Skill

@dataclass
class RuntimeContext:
    question: str
    reviewed_df: Optional[pd.DataFrame] = None
    intent: Optional[str] = None
    skill: Optional[Skill] = None
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    trace: List[str] = field(default_factory=list)

    def add_trace(self, message: str) -> None:
        """Appends a tracing log entry for execution observability."""
        self.trace.append(message)

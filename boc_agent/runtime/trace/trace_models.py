import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ConfidenceSnapshot(BaseModel):
    stage: str
    confidence: float
    note: str

class ReasoningStep(BaseModel):
    stage: str
    action: str
    note: str

class ToolTrace(BaseModel):
    tool_name: str
    start_time: float
    end_time: float
    duration_ms: float
    status: str
    rows_accessed: int
    dataframe_required: bool
    dataframe_present: bool
    mutation_attempted: bool = False
    execution_allowed: bool

class PlannerTrace(BaseModel):
    original_query: str
    intent: str
    reason: str
    capability: str
    tool_selected: str

class ResponseMetadata(BaseModel):
    response_type: str
    response_length: int
    response_timestamp: str
    grounding_source: str
    citations_used: List[str] = Field(default_factory=list)
    skill_version: str
    runtime_version: str

class RuntimeTrace(BaseModel):
    trace_id: str
    timestamp: str
    user_query: str
    planner: PlannerTrace
    reasoning: List[ReasoningStep] = Field(default_factory=list)
    tools: List[ToolTrace] = Field(default_factory=list)
    latency_ms: Dict[str, float] = Field(default_factory=dict)
    confidence_history: List[ConfidenceSnapshot] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    response: str
    metadata: ResponseMetadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary using standard Pydantic serialization."""
        if hasattr(self, "model_dump"):
            return self.model_dump()
        return self.dict()

    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert trace to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

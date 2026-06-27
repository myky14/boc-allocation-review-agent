import uuid
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from boc_agent.runtime.trace.trace_models import (
    RuntimeTrace,
    PlannerTrace,
    ToolTrace,
    ReasoningStep,
    ConfidenceSnapshot,
    ResponseMetadata
)

class TraceBuilder:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.user_query = ""
        self.planner: Optional[PlannerTrace] = None
        self.reasoning: List[ReasoningStep] = []
        self.tools: List[ToolTrace] = []
        self.latency_ms: Dict[str, float] = {}
        self.confidence_history: List[ConfidenceSnapshot] = []
        self.start_times: Dict[str, float] = {}

    def start_stage(self, stage: str):
        """Start measuring duration for a stage using monotonic timer."""
        self.start_times[stage] = time.perf_counter()

    def end_stage(self, stage: str):
        """End measuring duration for a stage and save latency in ms."""
        if stage in self.start_times:
            duration = (time.perf_counter() - self.start_times[stage]) * 1000.0
            self.latency_ms[stage] = duration

    def set_user_query(self, user_query: str):
        """Set the user's original query."""
        self.user_query = user_query

    def set_planner(self, original_query: str, intent: str, reason: str, capability: str, tool_selected: str):
        """Set the planner trace attributes."""
        self.planner = PlannerTrace(
            original_query=original_query,
            intent=intent,
            reason=reason,
            capability=capability,
            tool_selected=tool_selected
        )

    def add_reasoning_step(self, stage: str, action: str, note: str):
        """Add a reasoning step in the deterministic graph."""
        self.reasoning.append(ReasoningStep(stage=stage, action=action, note=note))

    def add_tool_trace(self, tool_name: str, start_time: float, end_time: float, status: str,
                       rows_accessed: int, dataframe_required: bool, dataframe_present: bool,
                       execution_allowed: bool, mutation_attempted: bool = False):
        """Add trace entry for a tool execution."""
        duration_ms = (end_time - start_time) * 1000.0
        self.tools.append(ToolTrace(
            tool_name=tool_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            status=status,
            rows_accessed=rows_accessed,
            dataframe_required=dataframe_required,
            dataframe_present=dataframe_present,
            mutation_attempted=mutation_attempted,
            execution_allowed=execution_allowed
        ))

    def add_confidence_snapshot(self, stage: str, confidence: float, note: str):
        """Add a confidence checkpoint in the confidence timeline."""
        self.confidence_history.append(ConfidenceSnapshot(stage=stage, confidence=confidence, note=note))

    def build(self, response: str, response_type: str, grounding_source: str,
              citations_used: List[str], skill_version: str, runtime_version: str,
              errors: Optional[List[str]] = None) -> RuntimeTrace:
        """Assembles and returns the final RuntimeTrace object."""
        metadata = ResponseMetadata(
            response_type=response_type,
            response_length=len(response),
            response_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            grounding_source=grounding_source,
            citations_used=citations_used,
            skill_version=skill_version,
            runtime_version=runtime_version
        )
        if "total" not in self.latency_ms and "run" in self.start_times:
            self.latency_ms["total"] = (time.perf_counter() - self.start_times["run"]) * 1000.0

        if not self.planner:
            self.planner = PlannerTrace(
                original_query=self.user_query,
                intent="unknown",
                reason="Default fallback initialization",
                capability="unknown",
                tool_selected="unknown_fallback"
            )

        return RuntimeTrace(
            trace_id=self.trace_id,
            timestamp=self.timestamp,
            user_query=self.user_query,
            planner=self.planner,
            reasoning=self.reasoning,
            tools=self.tools,
            latency_ms=self.latency_ms,
            confidence_history=self.confidence_history,
            errors=errors or [],
            response=response,
            metadata=metadata
        )

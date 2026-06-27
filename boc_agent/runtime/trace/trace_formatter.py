from boc_agent.runtime.trace.trace_models import RuntimeTrace

def format_trace_to_markdown(trace: RuntimeTrace) -> str:
    """Formats the RuntimeTrace into a clear, structured markdown timeline for verification or debug viewing."""
    lines = []
    lines.append(f"### 🔍 Execution Trace Timeline (ID: `{trace.trace_id}`)")
    lines.append(f"- **Timestamp**: `{trace.timestamp}`")
    lines.append(f"- **User Query**: *\"{trace.user_query}\"*")
    lines.append(f"- **Latency (Total)**: `{trace.latency_ms.get('total', 0.0):.2f} ms` (Planner: `{trace.latency_ms.get('planner', 0.0):.2f} ms`, Executor: `{trace.latency_ms.get('executor', 0.0):.2f} ms`)")
    lines.append("")
    lines.append("#### 🧭 Planner Routing Decision")
    p = trace.planner
    lines.append(f"- **Intent**: `{p.intent}`")
    lines.append(f"- **Capability Required**: `{p.capability}`")
    lines.append(f"- **Selected Tool**: `{p.tool_selected}`")
    lines.append(f"- **Reasoning**: *{p.reason}*")
    lines.append("")
    lines.append("#### 🧠 Deterministic Reasoning Path")
    for idx, step in enumerate(trace.reasoning, 1):
        lines.append(f"{idx}. **{step.stage}**: {step.action} (*{step.note}*)")
    lines.append("")
    lines.append("#### 🛠️ Tool Execution Log")
    if not trace.tools:
        lines.append("No tools executed.")
    for tool in trace.tools:
        lines.append(f"- **Tool**: `{tool.tool_name}` (Allowed: `{tool.execution_allowed}`, Status: `{tool.status}`)")
        lines.append(f"  - **Duration**: `{tool.duration_ms:.2f} ms`")
        lines.append(f"  - **Dataframe Required / Present**: `{tool.dataframe_required}` / `{tool.dataframe_present}`")
        lines.append(f"  - **Rows Accessed**: `{tool.rows_accessed}`")
    lines.append("")
    lines.append("#### 📈 Confidence Timeline")
    for conf in trace.confidence_history:
        lines.append(f"- **{conf.stage}**: `{conf.confidence:.2f}` (*{conf.note}*)")
    lines.append("")
    lines.append("#### 📦 Response Metadata")
    m = trace.metadata
    lines.append(f"- **Response Type**: `{m.response_type}` (Length: `{m.response_length}` chars)")
    lines.append(f"- **Grounding Source**: `{m.grounding_source}`")
    lines.append(f"- **Skill Version / Runtime Version**: `{m.skill_version}` / `{m.runtime_version}`")
    return "\n".join(lines)

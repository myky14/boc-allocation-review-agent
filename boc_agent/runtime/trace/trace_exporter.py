import os
from boc_agent.runtime.trace.trace_models import RuntimeTrace

def export_trace(trace: RuntimeTrace, output_path: str = "outputs/runtime_trace.json") -> None:
    """Writes the RuntimeTrace to a local JSON file for observability."""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(trace.to_json(indent=2))

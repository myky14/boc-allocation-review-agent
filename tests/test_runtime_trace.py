import os
import json
import pytest
import pandas as pd
from boc_agent.runtime.agent import BOCReviewAgent
from boc_agent.runtime.context import RuntimeContext
from boc_agent.runtime.trace.trace_models import RuntimeTrace
from boc_agent.runtime.trace.trace_exporter import export_trace
from boc_agent.runtime.trace.trace_formatter import format_trace_to_markdown
from boc_agent.chat.assistant import ReviewConversationAssistant

def _get_test_df():
    data = [
        {
            "trans_ref": "508841",
            "vendor_name": "Theo Desjardins",
            "amount": 100.0,
            "currency": "CAD",
            "application_province": "Quebec",
            "location": "920",
            "ep": "55",
            "suggested_allocation_column": "Quebec non-qualified",
            "eligibility_status": "Ineligible",
            "review_status": "Needs Human Review",
            "confidence_score": 0.70,
            "rationale": "Quebec non-qualified cost (Location 920)",
            "secondary_allocation_note": "None"
        }
    ]
    return pd.DataFrame(data)

def test_public_api_string_return_and_last_trace_populated():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    # 1. BOCReviewAgent.run() returns str.
    assert isinstance(res, str)
    assert "Workbook Summary Metrics" in res
    # 2. BOCReviewAgent.last_trace is populated after run.
    assert agent.last_trace is not None
    assert isinstance(agent.last_trace, RuntimeTrace)

def test_assistant_api_string_return_and_last_trace_populated():
    assistant = ReviewConversationAssistant()
    df = _get_test_df()
    res = assistant.answer("summary", df)
    # 3. ReviewConversationAssistant.answer() returns str.
    assert isinstance(res, str)
    # 4. ReviewConversationAssistant.last_trace is populated after answer.
    assert assistant.last_trace is not None
    assert isinstance(assistant.last_trace, RuntimeTrace)

def test_streamlit_compatible_call_path():
    # 5. Streamlit-compatible call path remains string-only.
    assistant = ReviewConversationAssistant()
    df = _get_test_df()
    res = assistant.answer("What is Location 920?", df)
    assert isinstance(res, str)

def test_found_row_explanation_trace():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("explain transaction 508841", df)
    trace = agent.last_trace
    # 1. Found row explanation trace has rows_accessed=1.
    assert trace.tools[0].rows_accessed == 1
    assert "Theo Desjardins" in res

def test_missing_row_explanation_trace():
    agent = BOCReviewAgent()
    df = _get_test_df()
    # 3. Missing row explanation still returns safe not-found/run-review-first response.
    res = agent.run("explain transaction 999999", df)
    trace = agent.last_trace
    # 2. Missing row explanation trace has rows_accessed=0.
    assert trace.tools[0].rows_accessed == 0
    assert "Transaction not found" in res

def test_planner_trace_populated():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    assert trace.planner is not None
    assert trace.planner.original_query == "summary"
    assert trace.planner.intent == "summary"
    assert "summary" in trace.planner.reason.lower()
    assert trace.planner.capability == "aggregate_stats"
    assert trace.planner.tool_selected == "dataframe_summary"

def test_tool_trace_recorded():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    assert len(trace.tools) == 1
    tool = trace.tools[0]
    assert tool.tool_name == "dataframe_summary"
    assert tool.start_time <= tool.end_time
    assert tool.duration_ms >= 0.0
    assert tool.status == "success"
    assert tool.rows_accessed == 1
    assert tool.dataframe_required is True
    assert tool.dataframe_present is True
    assert tool.mutation_attempted is False
    assert tool.execution_allowed is True

def test_reasoning_path_deterministic():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("explain transaction 508841", df)
    trace = agent.last_trace
    assert len(trace.reasoning) >= 3
    stages = [step.stage for step in trace.reasoning]
    assert "Agent Runtime" in stages
    assert "Planner" in stages
    assert "Executor" in stages
    assert "Formatter" in stages

def test_confidence_timeline_populated():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("explain transaction 508841", df)
    trace = agent.last_trace
    assert len(trace.confidence_history) >= 3
    stages = [conf.stage for conf in trace.confidence_history]
    assert "Planner" in stages
    assert "Tool Selection" in stages
    assert "Row Match" in stages
    assert "Formatter" in stages

def test_latency_values_valid():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    assert trace.latency_ms.get("planner", -1) >= 0.0
    assert trace.latency_ms.get("executor", -1) >= 0.0
    assert trace.latency_ms.get("formatter", -1) >= 0.0
    assert trace.latency_ms.get("total", -1) >= 0.0

def test_trace_serialization():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    d = trace.to_dict()
    assert d["trace_id"] == trace.trace_id
    j = trace.to_json()
    parsed = json.loads(j)
    assert parsed["trace_id"] == trace.trace_id

def test_trace_export(tmp_path):
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    out_file = tmp_path / "test_trace.json"
    export_trace(trace, str(out_file))
    assert os.path.exists(out_file)
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["trace_id"] == trace.trace_id

def test_last_trace_updated():
    agent = BOCReviewAgent()
    assistant = ReviewConversationAssistant()
    df = _get_test_df()

    res = assistant.answer("summary", df)
    assert assistant.last_trace is not None
    assert ReviewConversationAssistant.last_trace is not None
    assert ReviewConversationAssistant.last_trace.user_query == "summary"

def test_trace_does_not_expose_hidden_reasoning():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    j = trace.to_json()
    assert "thought" not in j.lower()
    assert "secret" not in j.lower()

def test_non_mutation_verified():
    agent = BOCReviewAgent()
    df = _get_test_df()
    df_orig = df.copy()
    agent.run("summary", df)
    pd.testing.assert_frame_equal(df, df_orig)

def test_skill_metadata_captured():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    assert trace.metadata.skill_version != "unknown"
    assert trace.metadata.skill_version == "1.0.0"

def test_rag_trace_captured():
    agent = BOCReviewAgent()
    res = agent.run("Explain the human in the loop workflow", None)
    trace = agent.last_trace
    assert trace.planner.intent == "rag"
    assert trace.planner.capability == "documentation_rag"
    assert trace.planner.tool_selected == "documentation_rag"
    assert trace.metadata.response_type == "rag_response"
    assert trace.metadata.grounding_source == "repository_documentation"

def test_row_lookup_trace_captured():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("explain transaction 508841", df)
    trace = agent.last_trace
    assert trace.planner.intent == "row_explanation"
    assert trace.planner.tool_selected == "row_explanation"
    assert len(trace.tools) == 1
    assert trace.tools[0].rows_accessed == 1

def test_summary_trace_captured():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    assert trace.planner.intent == "summary"
    assert trace.planner.tool_selected == "dataframe_summary"

def test_configuration_failure_trace(monkeypatch, tmp_path):
    monkeypatch.setenv("BOC_SKILL_FILE_PATH", str(tmp_path / "nonexistent.md"))
    from boc_agent.skill.loader import SkillLoader
    SkillLoader()._cached_skill = None

    agent = BOCReviewAgent()
    res = agent.run("summary", None)
    trace = agent.last_trace
    assert "configuration is unavailable or invalid" in res
    assert trace.metadata.response_type == "error"
    assert len(trace.errors) > 0

def test_missing_dataframe_trace():
    agent = BOCReviewAgent()
    res = agent.run("summary", None)
    trace = agent.last_trace
    assert "No reviewed workbook data is currently loaded" in res
    assert len(trace.tools) == 1
    tool = trace.tools[0]
    assert tool.status == "missing_dataframe"
    assert tool.execution_allowed is False

def test_refusal_trace():
    agent = BOCReviewAgent()
    res = agent.run("optimize my tax credit officially", None)
    trace = agent.last_trace
    assert trace.planner.intent == "tax_ruling"
    assert trace.planner.tool_selected == "tax_refusal"
    assert trace.metadata.response_type == "refusal"

def test_runtime_version_included():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    assert trace.metadata.runtime_version == "1.0.0"

def test_trace_formatter():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    trace = agent.last_trace
    md = format_trace_to_markdown(trace)
    assert "Execution Trace Timeline" in md
    assert "Planner Routing Decision" in md
    assert "Confidence Timeline" in md

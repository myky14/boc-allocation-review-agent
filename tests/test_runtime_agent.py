import os
import pytest
import pandas as pd
from boc_agent.runtime.agent import BOCReviewAgent
from boc_agent.runtime.context import RuntimeContext
from boc_agent.runtime.planner import Planner
from boc_agent.runtime.tool_registry import ToolRegistry, RuntimeTool
from boc_agent.runtime.executor import Executor
from boc_agent.chat.assistant import ReviewConversationAssistant
from boc_agent.skill.models import Skill, SkillMetadata, ToolDefinition, GroundingPolicy

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
        },
        {
            "trans_ref": "123456",
            "vendor_name": "Greenslate Pay",
            "amount": 500.0,
            "currency": "CAD",
            "application_province": "Ontario",
            "location": "900",
            "ep": "41",
            "suggested_allocation_column": "Ontario Salary (41)",
            "eligibility_status": "Eligible",
            "review_status": "Approved",
            "confidence_score": 1.00,
            "rationale": "Ontario salary eligible",
            "secondary_allocation_note": "None"
        }
    ]
    return pd.DataFrame(data)

def _get_mock_skill() -> Skill:
    metadata = SkillMetadata(
        name="test_skill",
        version="1.0.0",
        description="test",
        role="test"
    )
    grounding = GroundingPolicy(
        strict_grounding=True,
        omit_protocols=["file:///"],
        path_style="relative",
        required_disclaimer="Grounding disclaimer"
    )
    tools = [
        ToolDefinition(name="classification_tool", intents=["row_explanation"], mutating=False, required_dataframe=True),
        ToolDefinition(name="eligibility_tool", intents=["row_explanation", "ineligible_summary", "needs_documentation", "filter_location"], mutating=False, required_dataframe=True),
        ToolDefinition(name="allocation_tool", intents=["row_explanation"], mutating=False, required_dataframe=True),
        ToolDefinition(name="RAG_retriever", intents=["rag"], mutating=False, required_dataframe=False, required_grounding=True)
    ]
    return Skill(
        metadata=metadata,
        capabilities=["dataframe_lookup", "aggregate_stats", "documentation_rag"],
        non_capabilities=[],
        tools=tools,
        refusal_rules=[],
        grounding_policy=grounding
    )


# 1. BOCReviewAgent answers summary question with dataframe.
def test_agent_answers_summary_with_df():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    assert "Workbook Summary Metrics" in res
    assert "Total Transactions" in res


# 2. BOCReviewAgent answers row explanation with dataframe.
def test_agent_answers_row_explanation_with_df():
    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("explain transaction 508841", df)
    assert "Transaction Details: Reference 508841" in res
    assert "Theo Desjardins" in res


# 3. BOCReviewAgent answers RAG documentation question without dataframe.
def test_agent_answers_rag_without_df():
    agent = BOCReviewAgent()
    # "Explain the HITL process" should trigger RAG and work without a DataFrame
    res = agent.run("Explain the HITL process", None)
    assert "Documentation Reference" in res or "No relevant repository documentation was found" in res


# 4. Row question without dataframe returns run-review-first response.
def test_agent_row_explanation_without_df_denial():
    agent = BOCReviewAgent()
    res = agent.run("explain transaction 508841", None)
    assert "Transaction not found / run review first" in res


# 5. Unknown question returns safe fallback.
def test_agent_unknown_question_fallback():
    agent = BOCReviewAgent()
    res = agent.run("What is the temperature in Calgary?", None)
    assert "couldn't classify your question" in res or "Please rephrase your question" in res


# 6. Tax/legal question returns refusal.
def test_agent_tax_refusal():
    agent = BOCReviewAgent()
    res = agent.run("optimize my tax credit officially", None)
    assert "Official Determination Disclaimer" in res


# 7. Runtime does not mutate dataframe.
def test_agent_runtime_non_mutation():
    agent = BOCReviewAgent()
    df = _get_test_df()
    df_orig = df.copy()
    agent.run("summary", df)
    agent.run("explain transaction 508841", df)
    pd.testing.assert_frame_equal(df, df_orig)


# 8. Planner sets expected intents.
def test_planner_sets_intents():
    planner = Planner()

    # Test cases mapping questions to intents
    queries = {
        "summary": "summary",
        "explain transaction 123456": "row_explanation",
        "Show me all Location 920 rows": "filter_location",
        "is this officially eligible?": "tax_ruling",
        "Explain the human in the loop workflow": "rag",
        "this is a completely random query that should be unknown": "unknown"
    }

    for q, expected_intent in queries.items():
        ctx = RuntimeContext(question=q)
        planner.plan(ctx)
        assert ctx.intent == expected_intent
        assert len(ctx.trace) > 0


# 9. ToolRegistry resolves expected tools for major intents.
def test_registry_resolves_tools():
    registry = ToolRegistry()

    assert registry.get_tool_for_intent("summary").name == "dataframe_summary"
    assert registry.get_tool_for_intent("row_explanation").name == "row_explanation"
    assert registry.get_tool_for_intent("filter_location").name == "location_filter"
    assert registry.get_tool_for_intent("ineligible_summary").name == "status_filter"
    assert registry.get_tool_for_intent("rag").name == "documentation_rag"
    assert registry.get_tool_for_intent("tax_ruling").name == "tax_refusal"
    assert registry.get_tool_for_intent("unknown").name == "unknown_fallback"


# 10. Executor blocks dataframe-required tool when dataframe missing.
def test_executor_blocks_df_required_when_missing():
    registry = ToolRegistry()
    executor = Executor(registry)

    skill = _get_mock_skill()
    ctx = RuntimeContext(question="summary", intent="summary", reviewed_df=None, skill=skill)
    res = executor.execute(ctx)
    assert "Transaction not found / run review first" in res
    assert any("missing DataFrame" in t for t in ctx.trace)


# 11. Executor blocks mutating tool.
def test_executor_blocks_mutating_tool():
    registry = ToolRegistry()
    # Register a dummy mutating tool
    registry.register(RuntimeTool(
        name="mutating_tool",
        purpose="Mutates the ledger",
        supported_intents=["mutate"],
        handler=lambda ctx: "Done",
        mutating=True,
        requires_dataframe=False
    ))

    executor = Executor(registry)
    skill = _get_mock_skill()
    ctx = RuntimeContext(question="mutate", intent="mutate", skill=skill)
    res = executor.execute(ctx)
    assert "Tool permission denied" in res
    assert "mutating" in res.lower()


# 12. Skill permission check blocks unsupported tool/intent.
def test_executor_skill_permission_denial():
    registry = ToolRegistry()
    executor = Executor(registry)

    # Construct a skill that doesn't permit classification_tool
    metadata = SkillMetadata(name="restricted_skill", version="1.0.0", description="test", role="test")
    grounding = GroundingPolicy(strict_grounding=True, omit_protocols=[], required_disclaimer="Disclaimer")

    # classification_tool only supports "other_intent" instead of "row_explanation"
    bad_tools = [
        ToolDefinition(name="classification_tool", intents=["other_intent"], mutating=False, required_dataframe=True)
    ]
    restricted_skill = Skill(
        metadata=metadata,
        capabilities=["dataframe_lookup"],
        tools=bad_tools,
        grounding_policy=grounding
    )

    df = _get_test_df()
    ctx = RuntimeContext(
        question="explain transaction 508841",
        intent="row_explanation",
        reviewed_df=df,
        skill=restricted_skill
    )

    res = executor.execute(ctx)
    assert "Tool permission denied" in res
    assert "classification_tool" in res


# 13. ReviewConversationAssistant delegates to BOCReviewAgent.
def test_assistant_delegates_to_agent():
    assistant = ReviewConversationAssistant()
    df = _get_test_df()
    res = assistant.answer("summary", df)
    assert "Workbook Summary Metrics" in res


# 14. Existing Phase 8.1/8.2 chat behavior remains compatible.
def test_compatibility_retains_behavior():
    assistant = ReviewConversationAssistant()
    df = _get_test_df()

    # Test Location 920 filter
    res = assistant.answer("Show me all Location 920 rows", df)
    assert "Location 920 Breakdown" in res

    # Test ineligible summary
    res = assistant.answer("Show ineligible rows", df)
    assert "Ineligible Costs Summary" in res


# 15. Trace list records planner/executor steps.
def test_trace_list_records_execution_steps():
    agent = BOCReviewAgent()
    df = _get_test_df()

    # Create context explicitly to inspect trace
    skill = _get_mock_skill()
    ctx = RuntimeContext(
        question="explain transaction 508841",
        reviewed_df=df,
        skill=skill
    )

    agent.planner.plan(ctx)
    assert ctx.intent == "row_explanation"
    assert any("Planner" in t for t in ctx.trace)

    res = agent.executor.execute(ctx)
    assert "Transaction Details" in res
    assert any("Executor" in t for t in ctx.trace)

    # Verify trace contains execution milestones
    trace_str = " ".join(ctx.trace)
    assert "resolved intent" in trace_str.lower()
    assert "resolved tool" in trace_str.lower()
    assert "invoking handler" in trace_str.lower()


# 16. Missing skill path blocks execution.
def test_missing_skill_path_blocks_execution(monkeypatch, tmp_path):
    monkeypatch.setenv("BOC_SKILL_FILE_PATH", str(tmp_path / "nonexistent_skill.md"))
    from boc_agent.skill.loader import SkillLoader
    SkillLoader()._cached_skill = None

    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    assert "Skill configuration is unavailable or invalid" in res


# 17. Invalid skill file blocks execution.
def test_invalid_skill_file_blocks_execution(monkeypatch, tmp_path):
    invalid_file = tmp_path / "invalid_skill.md"
    with open(invalid_file, "w", encoding="utf-8") as f:
        f.write("garbage content that is not valid YAML frontmatter")
    monkeypatch.setenv("BOC_SKILL_FILE_PATH", str(invalid_file))
    from boc_agent.skill.loader import SkillLoader
    SkillLoader()._cached_skill = None

    agent = BOCReviewAgent()
    df = _get_test_df()
    res = agent.run("summary", df)
    assert "Skill configuration is unavailable or invalid" in res


# 18. User gets safe configuration error.
def test_safe_configuration_error_no_stack_trace(monkeypatch, tmp_path):
    monkeypatch.setenv("BOC_SKILL_FILE_PATH", str(tmp_path / "missing.md"))
    from boc_agent.skill.loader import SkillLoader
    SkillLoader()._cached_skill = None

    agent = BOCReviewAgent()
    res = agent.run("summary", None)
    assert "Skill configuration is unavailable or invalid" in res
    assert "Runtime execution has been blocked for safety" in res


# 19. Valid root SKILL.md still allows normal summary/RAG/row flows.
def test_valid_root_skill_allows_normal_flows(monkeypatch):
    monkeypatch.setenv("BOC_SKILL_FILE_PATH", "SKILL.md")
    from boc_agent.skill.loader import SkillLoader
    SkillLoader()._cached_skill = None

    agent = BOCReviewAgent()
    df = _get_test_df()

    res_summary = agent.run("summary", df)
    assert "Workbook Summary Metrics" in res_summary

    res_explain = agent.run("explain transaction 508841", df)
    assert "Transaction Details: Reference 508841" in res_explain

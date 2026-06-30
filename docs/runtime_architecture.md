# ADK-Inspired Runtime Architecture

This document describes the implemented **ADK-inspired local runtime architecture** for the **BOC Allocation Review Agent**, showing how the system has evolved from a single assistant-centered class to a modular, Google Agent Development Kit (ADK) inspired runtime.

---

## 1. Purpose

Previously, natural language queries were routed directly through a single assistant class which served as the router, database filter, RAG retriever, and output formatter.

### Previous Flow (Phase 8.1 / 8.2)
```
User
  ↓
ReviewConversationAssistant
  ↓
query_router
  ↓
DataFrame logic / RAG / refusal / response formatting
```

To align with modern AI Agent practices and prepare the application for seamless future migration to the Google Agent Development Kit (ADK), we have implemented a dedicated local runtime layer.

### Target Flow
```
User
  ↓
  ↓
Planner
  ↓
RuntimeContext
  ↓
ToolRegistry
  ↓
Executor
  ↓
ResponseBuilder
```

This evolution:
- **Separates Concerns**: De-couples intent routing (planning) from tool execution and response formatting.
- **Enforces Safety at the Runtime Level**: Integrates `SKILL.md` capability checks and execution constraints natively within the agent boundary.
- **Improves Testability**: Individual modules (Planner, Executor, Registry) can be unit-tested without loading the entire Streamlit dashboard or reading dataframes.

---

## 2. Target Runtime Components

The local runtime package is structured under `boc_agent/runtime/`:

```text
boc_agent/runtime/
  ├── __init__.py
  ├── agent.py
  ├── planner.py
  ├── executor.py
  ├── tool_registry.py
  ├── context.py
  └── response.py
```

### Module Specifications

| Module | Responsibility | Primary Inputs | Primary Outputs | Relationship to Existing Code |
| --- | --- | --- | --- | --- |
| `agent.py` | Core agent entry point | Raw question, reviewed DataFrame | Formatted Response Markdown | Replaces the entry orchestration of the conversational assistant. |
| `planner.py` | Intent classification & capability mapping | User question, active Skill config | Intent name, Target Tool reference | Calls `query_router.py` and validates against `SKILL.md` capabilities. |
| `context.py` | Execution state container | Question, DataFrame, Skill State | Instantiated Context object | Consolidates variables previously passed ad-hoc between methods. |
| `tool_registry.py` | Tool metadata indexing | Tool registration calls | Registered Tool instances | Maps available rules, filters, and retrievers to intent keys. |
| `executor.py` | Permission enforcement & tool invocation | Context, Tool reference | Raw tool outputs (e.g. rows/excerpts) | Enforces mutating checks and grounding constraints from `SKILL.md`. |
| `response.py` | Output formatting & disclaimer injection | Tool output, Grounding Policy | Sanitized markdown response | Wraps `response_templates.py` and applies path sanitization. |

---

## 3. Runtime Component Responsibilities

### `BOCReviewAgent`
- Exposes a public `run(question, reviewed_df=None) -> str` method.
- Saves the generated structured trace to the `last_trace` property.
- Operates as a thin wrapper on top of the runtime execution pipeline.
- Implements a compatibility layer to ensure that Streamlit dashboard calls do not break.

### `Planner`
- Uses the keyword-based `query_router.py` to identify the user's intent.
- Validates the mapped intent against the permitted capabilities in `SKILL.md` (e.g. checking that a dataframe query is only routed if `dataframe_lookup` is enabled).

### `RuntimeContext`
- Instantiated at the start of each agent run.
- Stores the active transaction DataFrame, the raw question, loaded skill attributes, execution timestamps, and intermediate intent routing states.

### `ToolRegistry`
- A central directory mapping intents to execution functions.
- Prevents the invocation of arbitrary or unregistered code by requiring explicit tool registration during startup.

### `Executor`
- Intercepts executions to check `SKILL.md` tool permissions.
- Prevents mutating actions (verifying `mutating: false`).
- Asserts that required dataframes are present before triggering row lookups.

### `ResponseBuilder`
- Takes the raw output from the executor and applies formatting templates.
- Dynamically loads the `RequiredDisclaimer` text and sanitizes local path formats to comply with the skill's grounding policy.

---

## 4. Runtime Data Flow

The runtime processes user requests according to the following sequential flow:

```
[ User Query ]
      │
      ▼
1. Agent.run(question, df) ──► Instantiates [ RuntimeContext ]
      │
      ▼
2. Planner.plan(question) ──► Routes query to intent (e.g. "rag")
      │
      ▼
3. Skill Validation ──► Checks if intent is in whitelisted capabilities
      │
      ▼
4. ToolRegistry ──► Resolves intent to target tool ("RAG_retriever")
      │
      ▼
5. Executor.run() ──► Checks mutating / dataframe / grounding permissions
      │
      ▼
6. Tool Execution ──► Executes tool logic (retrieves document chunks)
      │
      ▼
7. ResponseBuilder ──► Enforces relative paths & disclaimer text
      │
      ▼
[ Formatted Markdown Answer Returned to Streamlit / CLI ]
```

---

## 5. Tool Lifecycle

Every tool registered in `ToolRegistry` implements a standard metadata structure:

- `name`: Unique identifier matching the `SKILL.md` available tool list (e.g. `classification_tool`).
- `purpose`: Human-readable description of what the tool executes.
- `supported_intents`: List of routed intents allowed to trigger this tool (e.g. `["row_explanation"]`).
- `mutating`: Boolean flag indicating if the tool modifies workbook states (strictly `False` for review MVP).
- `requires_dataframe`: Boolean indicating if a loaded ledger DataFrame must be present.
- `requires_grounding`: Boolean indicating if document grounding policies apply to outputs.
- `handler`: Mapped reference to the underlying specialist logic.
- `failure_behavior`: Error response pattern if execution fails (e.g. raise vs fallback string).

### Active Tools Registered:
1. **Row Lookup Specialist**: Wraps vendor/Trans Ref search filters.
2. **Workbook Statistics Specialist**: Wraps overall counts and status distributions.
3. **Queue Summary Specialist**: Filters rows matching needs-review states.
4. **Documentation RAG Specialist**: Searches local Markdown documentation chunks.

---

## 6. Safety and Permission Flow

- **Contract Governance**: The `SKILL.md` file remains the configuration authority for what the agent is permitted to execute. If a capability or tool intent is omitted in `SKILL.md`, it is immediately blocked at runtime.
- **Rule Core Isolation**: The deterministic accounting rules (`allocation_tool.py`) are strictly read-only and isolated. The agent cannot modify rules or alter the logic engine's allocation suggestions.
- **Mutation Prevention**: Any tool declaring `mutating: true` fails validation at loader startup. The agent cannot alter data records; all human reviews and adjustments are captured in separate, designated columns (`human_` columns) outside the agent's control.
- **Grounding Restraints**: RAG retrieval is read-only. Responses are grounded strictly inside indexed repo files with relative links. Absolute paths (`file:///`) are programmatically scrubbed before output.

---

## 7. Compatibility Strategy

To ensure seamless integration in Phase 9.1:
- `ReviewConversationAssistant` in `boc_agent/chat/assistant.py` will be refactored into a thin compatibility shell. Its `answer()` method will instantiate and call `BOCReviewAgent.run()`.
- The Streamlit dashboard (`app.py`) will remain unmodified, continuing to call the assistant interface.
- CLI execution models and parsing pipelines will run unchanged.
- All 87 existing test scenarios must pass without modification.

---

## 8. Failure Modes

| Error Case | Runtime Response |
| --- | --- |
| Unknown Intent | Returns a helpful classification warning template requesting rephrasing. |
| Missing DataFrame | Returns `"No reviewed workbook data is currently loaded..."` for dataframe queries. |
| Skill Not Loaded | Raises a critical startup exception (fails fast to prevent running without safety rules). |
| Tool Not Registered | Aborts execution and returns a permission-denial message. |
| Permission Denied | Returns `"Tool permission denied: [ToolName] is not permitted for intent..."`. |
| RAG No Results | Returns `"No relevant repository documentation was found for this question."` |
| Security Violation | Intercepted by L1 guardrails; returns human-review warning and overrides confidence to 0. |
| Tool Execution Error | Catches exception gracefully and returns a safe fallback error message. |

---

## 9. Phase 9.1 Implementation Status

The ADK-inspired local runtime architecture has been fully implemented in Phase 9.1:
1. **Package Scaffolding**: Created `boc_agent/runtime/` with `__init__.py`.
2. **Context & Models Definition**: Implemented `context.py` containing the `RuntimeContext` class.
3. **Planner Hook-up**: Implemented `planner.py` wrapping the keyword router.
4. **Registry Setup**: Built `tool_registry.py` and registered the dataframe/RAG specialists.
5. **Executor Enforcement**: Implemented `executor.py` to enforce `SKILL.md` tool permissions and block mutating operations.
6. **Output Builder**: Implemented `response.py` with relative path sanitization.
7. **Assistant Refactoring**: Refactored `assistant.py` to wrap `BOCReviewAgent`.
8. **Runtime Test Suite**: Added a comprehensive unit test suite in `tests/test_runtime_agent.py`.
9. **Verification**: Ran all tests (130 passing) and verified backward compatibility.

---

## 10. Phase 9.2 Runtime Trace & Observability Status

The runtime trace and observability layer has been fully implemented in Phase 9.2:
- **Package structure**: Created `boc_agent/runtime/trace/` containing:
  * `trace_models.py`: Pydantic models for `RuntimeTrace`, `PlannerTrace`, `ToolTrace`, `ReasoningStep`, `ConfidenceSnapshot`, and `ResponseMetadata`.
  * `trace_builder.py`: Implements `TraceBuilder` to measure monotonicity latencies and log confidence metrics.
  * `trace_exporter.py`: Outputs traces to `outputs/runtime_trace.json`.
  * `trace_formatter.py`: Converts trace timelines to markdown layouts.
- **Trace Properties**:
  * **Planner Trace**: Logs intents, routing reasons, capabilities, and tool matching.
  * **Tool Trace**: Measures execution limits, DataFrame status, rows accessed, and blocks mutations.
  * **Reasoning Graph**: Charts sequential execution step milestones.
  * **Confidence Timeline**: Records confidence checkpoints (Planner, Tool Selection, Row Match, Formatter).
- **Agent integration**:
  * `BOCReviewAgent.run` returns a `str` response and stores the trace in `agent.last_trace`.
  * `ReviewConversationAssistant.answer` remains backward-compatible (returns string response) and stores the trace in `assistant.last_trace`.
- **Verification tests**: Added `tests/test_runtime_trace.py` (24 new tests, raising the total test count to 307).

---

## 11. Phase 10.1 Docker + Google Cloud Run Deployment Readiness

The local-first runtime has been containerized and prepared for cloud hosting in Phase 10.1:
- **Dockerfile**: Production-ready image configuration utilizing `uv` for package management, running headlessly on port `8080`, executing as non-root user `appuser`.
- **.dockerignore**: Excludes virtualenv and build caches while preserving synthetic ledger data and RAG repository documentation.
- **Deployment Guide**: [docs/deployment_cloud_run.md](deployment_cloud_run.md) provides detailed step-by-step commands to deploy the agent with strict resource constraints (`--min-instances 0 --max-instances 1`).
- **Observability Smoke Checks**: A container-ready [smoke_deployment.py](../scripts/smoke_deployment.py) verifies the agent runtime and skill configuration are fully functional.
- **Safety Tests**: Unit checks in `tests/test_deployment_files.py` verify that the port configurations are correct and no credentials are baked in.

---

## 12. Phase 10.2 Cost Guardrails & Budget Documentation

Phase 10.2 introduces cost-control procedures and billing guardrails for deploying the agent:
- **Cost Guardrails Guide**: [docs/cost_guardrails.md](cost_guardrails.md) provides Google Cloud Console budget setups, alert thresholds (including forecasted warnings), instance constraints, and storage/artifact monitoring checklists.
- **Safety checks**: Unit tests in `tests/test_cost_guardrails_docs.py` verify that the cost guide uses cautious disclaimers and avoids unsafe zero-cost or hard-cap claims.

---

## 13. Phase 10.3 Optional ADK / Vertex AI Migration Guide

Phase 10.3 provides a migration roadmap from the local-first execution environment to managed cloud options:
- **Migration Guide**: [docs/adk_vertex_migration.md](adk_vertex_migration.md) details Google ADK mapping, Vertex AI mapping, migration strategies, and risks.
- **Verification tests**: Added `tests/test_adk_migration_docs.py` to assert correct roadmapping vocabulary and prevent false deployment assertions.

---

## 14. Phase 11.1 Portfolio & Repository Polish

Phase 11.1 adds professional presentation and polish assets for portfolio review:
- **Case Study**: [docs/portfolio_case_study.md](portfolio_case_study.md) provides structured case study details.
- **Demo Script**: [docs/demo_script.md](demo_script.md) provides a presenter-ready 5-7 minute walkthrough script.
- **Release Checklist**: [docs/release_checklist.md](release_checklist.md) provides git tagging release procedures.
- **Interview prep**: [docs/interview_notes.md](interview_notes.md) outlines technical Q&A preparation.
- **Verification tests**: Added `tests/test_portfolio_docs.py` to assert presence of all files, links, and disclaimers.

---

## 15. Phase 11.2 Demo Assets / Screenshots / Video Guide

Phase 11.2 adds placeholders and capture checklists to prepare for capstone presentation:
- **Demo Assets structure**: Creates `assets/` subdirectory placeholders with `.gitkeep` anchors and safe capture rules in `assets/README.md`.
- **Screenshot Checklist**: [docs/screenshot_checklist.md](screenshot_checklist.md) details Streamlit dashboard, conversational assistant, and runtime trace capture targets.
- **Video Recording Guide**: [docs/video_recording_guide.md](video_recording_guide.md) outlines narration scripts and a 5-7 minute timeline structure.
- **Presentation Flow**: [docs/presentation_flow.md](presentation_flow.md) maps timelines for pitches and technical interviews.
- **Verification tests**: Added `tests/test_demo_assets_docs.py` to assert presence of all placeholders, links, and disclaimers.

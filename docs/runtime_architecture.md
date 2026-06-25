# ADK-Inspired Runtime Architecture

This document describes the design for the next major evolution of the **BOC Allocation Review Agent**, moving from the current assistant-centered design to a modular, Google Agent Development Kit (ADK) inspired runtime architecture.

> **Phase 9.0 status**: This is a design-only document. The `boc_agent/runtime/` package described here is planned for Phase 9.1 and is not implemented in the current repository.

---

## 1. Purpose

The current architecture routes natural language queries directly through a conversational assistant class which acts as router, database filter, RAG retriever, and formatter in a single block.

### Current Flow
```
User
  ↓
ReviewConversationAssistant
  ↓
query_router
  ↓
DataFrame logic / RAG / refusal / response formatting
```

To align with modern AI Agent practices and prepare the application for future migration to Google ADK concepts, this document designs a dedicated local runtime layer.

### Target Flow
```
User
  ↓
BOCReviewAgent
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

The planned Phase 9.1 runtime package would be structured under `boc_agent/runtime/`:

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
- `source_of_truth`: Mapped reference to the underlying deterministic specialist logic (e.g. `allocation_tool.py`).
- `failure_behavior`: Error response pattern if execution fails (e.g. raise vs fallback string).

### Planned Tools To Register:
1. **Row Lookup Specialist**: Wraps vendor/Trans Ref search filters.
2. **Workbook Statistics Specialist**: Wraps overall counts and status distributions.
3. **Queue Summary Specialist**: Filters rows matching needs-review states.
4. **Documentation RAG Specialist**: Searches local Markdown documentation chunks.

---

## 6. Safety and Permission Flow

- **Contract Governance**: The `SKILL.md` file remains the configuration authority for what the planned runtime is permitted to execute. If a capability or tool intent is omitted in `SKILL.md`, it should be blocked at runtime.
- **Rule Core Isolation**: The deterministic accounting rules (`allocation_tool.py`) are strictly read-only and isolated. The agent cannot modify rules or alter the logic engine's allocation suggestions.
- **Mutation Prevention**: Any tool declaring `mutating: true` fails validation at loader startup. The agent cannot alter data records; all human reviews and adjustments are captured in separate, designated columns (`human_` columns) outside the agent's control.
- **Grounding Restraints**: RAG retrieval is read-only. Responses are grounded strictly inside indexed repo files with relative links. Absolute paths and file protocols are programmatically scrubbed before output.

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

## 9. Future Phase 9.1 Implementation Roadmap

1. **Package Scaffolding**: Create `boc_agent/runtime/` with `__init__.py`.
2. **Context & Models Definition**: Implement `context.py` and dataclass models.
3. **Planner Hook-up**: Implement `planner.py` wrapping the query router.
4. **Registry Setup**: Build `tool_registry.py` and register the dataframe/RAG specialists.
5. **Executor Enforcement**: Implement `executor.py` to enforce `SKILL.md` tool parameters.
6. **Output Builder**: Implement `response.py` with relative path sanitization.
7. **Assistant Refactoring**: Refactor `assistant.py` to wrap `BOCReviewAgent`.
8. **Runtime Test Suite**: Add unit tests for registry, context, and executor permissions.
9. **Final Verification**: Run full regression testing against processed GL rows.

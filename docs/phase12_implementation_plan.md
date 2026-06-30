# Native Google ADK Migration Implementation Plan

This document establishes the phased implementation plan for migrating from the local ADK-inspired runtime to the native Google ADK framework.

> [!IMPORTANT]
> **Current Status & Disclaimer**:
> * **Not Implemented**: This document is a design and feasibility implementation plan only. The native ADK integration is not implemented, and Vertex AI / Gemini / Agent Engine services are not deployed.
> * **allocation_tool.py**: Remains unchanged and untouched.
> * **No Gemini Decision Power**: Gemini must not make final allocation or eligibility decisions.

---

## Phase 12.1: Native ADK Wrapper POC
* **Goal**: Build a minimal, isolated ADK wrapper around the existing `BOCReviewAgent` to demonstrate framework capability without altering active runtime behavior.
* **Scope**: Create an experimental wrapper module.
* **Files Likely Changed**:
  - `[NEW] experiments/adk_poc/adk_wrapper.py`
  - `[NEW] tests/test_adk_poc.py`
* **Safety Constraints**:
  - The wrapper must delegate core logic to the existing offline `BOCReviewAgent`.
  - No active Google Cloud API credentials or network connections are allowed during local test execution.
* **Tests Required**: Output parity test asserting that the ADK wrapper response matches `ReviewConversationAssistant.answer` response exactly.
* **Rollback Plan**: Delete `experiments/adk_poc/` folder.

---

## Phase 12.2: ADK Tool Registry Bridge
* **Goal**: Wrap local read-only deterministic capabilities (classification, database lookup) as ADK-decorated tools.
* **Scope**: Programmatically register current `ToolRegistry` items as ADK tools.
* **Files Likely Changed**:
  - `boc_agent/adk_bridge/tools_bridge.py`
* **Safety Constraints**:
  - All tools must remain read-only.
  - Assert that tool parameters are validated before execution.
* **Tests Required**: Assert that registered ADK tools return the exact same output format as the native rule engine.
* **Rollback Plan**: Disable ADK tool wrapper registration, falling back to the custom local `ToolRegistry`.

---

## Phase 12.3: Session / State Bridge
* **Goal**: Map custom `RuntimeContext` memory variables to the native ADK session state handler.
* **Scope**: Establish state synchronization adapter.
* **Files Likely Changed**:
  - `boc_agent/adk_bridge/session_adapter.py`
* **Safety Constraints**:
  - Do not cache raw transaction databases or sensitive client records in managed state memory.
* **Tests Required**: State isolation tests checking that variable modification in session memory does not affect rule engine state.
* **Rollback Plan**: Fall back to in-memory local dictionary context serialization.

---

## Phase 12.4: Trace Export Bridge
* **Goal**: Format and export local trace files to Cloud Logging and Google Cloud Trace.
* **Scope**: Create a trace exporter adapter.
* **Files Likely Changed**:
  - `boc_agent/runtime/trace/trace_exporter.py`
* **Safety Constraints**:
  - Redact sensitive data fields before calling export endpoints.
* **Tests Required**: Assert that trace payloads conform to the standard Google Cloud Trace format.
* **Rollback Plan**: Disable Cloud exporter, leaving only local file logging active.

---

## Phase 12.5: Optional Gemini Explanation Layer
* **Goal**: Integrate Gemini to summarize tax guidelines or explain deterministic outcomes.
* **Scope**: Add LLM retrieval context enhancer.
* **Files Likely Changed**:
  - `boc_agent/runtime/agent/explanation_layer.py`
* **Safety Constraints**:
  - **No decision delegation**: Gemini must not make allocation or eligibility decisions.
  - Restrict Gemini context strictly to the output of `allocation_tool.py`.
* **Tests Required**: Negative testing asserting that model attempts to override rule classifications are caught and rejected.
* **Rollback Plan**: Turn off explanation layers, returning static response templates.

---

## Phase 12.6: Optional Agent Platform / Agent Engine Deployment
* **Goal**: Deploy the ADK-wrapped agent to Vertex AI Agent Engine.
* **Scope**: Configure gcloud project deployment configurations.
* **Files Likely Changed**:
  - `docs/deployment_cloud_run.md`
  - `[NEW] agent_engine_config.yaml`
* **Safety Constraints**:
  - Restrict roles using user-specified service accounts.
  - Set strict monthly GCP budget limits.
* **Tests Required**: Remote regression suite verifying that the deployed agent behaves exactly like the local dry-run simulator.
* **Rollback Plan**: Delete Cloud Agent Engine deployment, routing traffic back to the Cloud Run Streamlit container.
